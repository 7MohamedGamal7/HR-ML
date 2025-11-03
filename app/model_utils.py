"""
أدوات النماذج - Model Utilities
يحتوي على وظائف بناء وتدريب وتقييم النماذج
"""

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
import joblib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from loguru import logger
import pandas as pd
import numpy as np

from app.config import (
    PROMOTION_MODEL_PATH, METRICS_PATH, MODEL_VERSION_PATH,
    RANDOM_STATE, N_ESTIMATORS, MAX_DEPTH, CV_FOLDS
)
from app.data_utils import build_preprocessor
from app.i18n import get_message


def build_and_train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_type: str = "random_forest",
    use_cross_validation: bool = True
) -> Pipeline:
    """
    بناء وتدريب النموذج - Build and train model

    Args:
        X_train: بيانات التدريب - Training features
        y_train: أهداف التدريب - Training targets
        model_type: نوع النموذج - Model type (random_forest, gradient_boosting)
        use_cross_validation: استخدام التحقق المتقاطع - Use cross-validation

    Returns:
        النموذج المدرب - Trained model
    """
    logger.info(get_message("training_started"))

    # بناء المعالج - Build preprocessor
    prep = build_preprocessor()

    # اختيار المصنف - Select classifier
    if model_type == "gradient_boosting":
        clf = GradientBoostingClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=5,
            random_state=RANDOM_STATE,
            verbose=0
        )
    else:  # random_forest (default)
        clf = RandomForestClassifier(
            n_estimators=N_ESTIMATORS,
            max_depth=MAX_DEPTH,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbose=0
        )

    # بناء خط الأنابيب - Build pipeline
    model = Pipeline(steps=[
        ("prep", prep),
        ("clf", clf)
    ])

    # التحقق المتقاطع - Cross-validation
    if use_cross_validation and len(X_train) > CV_FOLDS:
        try:
            cv_scores = cross_val_score(
                model, X_train, y_train,
                cv=CV_FOLDS,
                scoring='accuracy',
                n_jobs=-1
            )
            logger.info(f"درجات التحقق المتقاطع: {cv_scores}")
            logger.info(f"متوسط الدقة: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        except Exception as e:
            logger.warning(f"فشل التحقق المتقاطع: {e}")

    # تدريب النموذج - Train model
    model.fit(X_train, y_train)
    logger.info(get_message("training_completed"))

    return model


def evaluate(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    detailed: bool = True
) -> Dict[str, Any]:
    """
    تقييم النموذج - Evaluate model

    Args:
        model: النموذج - Model
        X_test: بيانات الاختبار - Test features
        y_test: أهداف الاختبار - Test targets
        detailed: تقييم مفصل - Detailed evaluation

    Returns:
        مقاييس الأداء - Performance metrics
    """
    # التنبؤ - Make predictions
    preds = model.predict(X_test)

    # المقاييس الأساسية - Basic metrics
    metrics = {
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
        "f1_score": float(f1_score(y_test, preds, zero_division=0))
    }

    # مقاييس إضافية - Additional metrics
    if detailed:
        try:
            # احتمالات التنبؤ - Prediction probabilities
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X_test)[:, 1]
                metrics["roc_auc"] = float(roc_auc_score(y_test, proba))

            # مصفوفة الارتباك - Confusion matrix
            cm = confusion_matrix(y_test, preds)
            metrics["confusion_matrix"] = cm.tolist()

            # تقرير التصنيف - Classification report
            report = classification_report(y_test, preds, output_dict=True)
            metrics["classification_report"] = report

        except Exception as e:
            logger.warning(f"فشل في حساب المقاييس الإضافية: {e}")

    # حفظ المقاييس - Save metrics
    try:
        with open(METRICS_PATH, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"فشل في حفظ المقاييس: {e}")

    logger.info(f"المقاييس: الدقة={metrics['accuracy']:.4f}, "
                f"الدقة الموجبة={metrics['precision']:.4f}, "
                f"الاستدعاء={metrics['recall']:.4f}, "
                f"F1={metrics['f1_score']:.4f}")

    return metrics


def save_model(
    model: Pipeline,
    model_path: Path = PROMOTION_MODEL_PATH,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    حفظ النموذج - Save model

    Args:
        model: النموذج - Model
        model_path: مسار الحفظ - Save path
        metadata: بيانات إضافية - Additional metadata
    """
    try:
        # حفظ النموذج - Save model
        joblib.dump(model, model_path)
        logger.info(f"تم حفظ النموذج في: {model_path}")

        # حفظ معلومات الإصدار - Save version info
        version_info = {
            "model_path": str(model_path),
            "saved_at": datetime.now().isoformat(),
            "model_type": type(model.named_steps['clf']).__name__,
            "metadata": metadata or {}
        }

        with open(MODEL_VERSION_PATH, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"فشل في حفظ النموذج: {e}")
        raise


def load_model(model_path: Path = PROMOTION_MODEL_PATH) -> Pipeline:
    """
    تحميل النموذج - Load model

    Args:
        model_path: مسار النموذج - Model path

    Returns:
        النموذج المحمل - Loaded model

    Raises:
        FileNotFoundError: إذا لم يوجد النموذج - If model not found
    """
    if not model_path.exists():
        logger.error(f"النموذج غير موجود: {model_path}")
        raise FileNotFoundError(get_message("model_not_found"))

    try:
        model = joblib.load(model_path)
        logger.info(f"تم تحميل النموذج من: {model_path}")
        return model
    except Exception as e:
        logger.error(f"فشل في تحميل النموذج: {e}")
        raise


def get_feature_importance(model: Pipeline) -> Dict[str, float]:
    """
    الحصول على أهمية المتغيرات - Get feature importance

    Args:
        model: النموذج - Model

    Returns:
        أهمية المتغيرات - Feature importance
    """
    try:
        clf = model.named_steps['clf']
        if hasattr(clf, 'feature_importances_'):
            importances = clf.feature_importances_

            # الحصول على أسماء المتغيرات - Get feature names
            prep = model.named_steps['prep']
            feature_names = []

            # المتغيرات الرقمية - Numerical features
            if 'num' in prep.named_transformers_:
                from app.config import NUMERICAL_COLS
                feature_names.extend(NUMERICAL_COLS)

            # المتغيرات الفئوية - Categorical features
            if 'cat' in prep.named_transformers_:
                cat_transformer = prep.named_transformers_['cat']
                if hasattr(cat_transformer.named_steps['onehot'], 'get_feature_names_out'):
                    cat_features = cat_transformer.named_steps['onehot'].get_feature_names_out()
                    feature_names.extend(cat_features)

            # دمج الأسماء والأهمية - Combine names and importance
            if len(feature_names) == len(importances):
                importance_dict = dict(zip(feature_names, importances.tolist()))
                # ترتيب حسب الأهمية - Sort by importance
                importance_dict = dict(sorted(
                    importance_dict.items(),
                    key=lambda x: x[1],
                    reverse=True
                ))
                return importance_dict

    except Exception as e:
        logger.warning(f"فشل في الحصول على أهمية المتغيرات: {e}")

    return {}

