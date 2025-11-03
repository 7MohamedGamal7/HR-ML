"""
موجه السياسات - Policies Router
يوفر نقاط نهاية لإدارة سياسات الشركة
"""

from fastapi import APIRouter, HTTPException, Query, File, UploadFile
from pydantic import BaseModel, Field
from typing import List, Optional
from loguru import logger
import PyPDF2
import docx
import io

from app.policy_manager import policy_manager
from app.i18n import get_message

router = APIRouter(prefix="/policies", tags=["السياسات - Policies"])


class PolicyCreate(BaseModel):
    """نموذج إنشاء سياسة - Policy creation model"""
    title: str = Field(..., description="عنوان السياسة - Policy title")
    content: str = Field(..., description="محتوى السياسة - Policy content")
    category: str = Field("general", description="فئة السياسة - Policy category")
    tags: Optional[List[str]] = Field(default=[], description="وسوم السياسة - Policy tags")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "سياسة الإجازات السنوية",
                "content": "يحق لكل موظف الحصول على 21 يوم إجازة سنوية مدفوعة الأجر...",
                "category": "leave",
                "tags": ["إجازات", "موارد بشرية"]
            }
        }


class PolicyUpdate(BaseModel):
    """نموذج تحديث سياسة - Policy update model"""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


@router.post("/")
async def create_policy(
    policy: PolicyCreate,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    إنشاء سياسة جديدة - Create new policy
    
    Args:
        policy: بيانات السياسة - Policy data
        lang: اللغة - Language
    
    Returns:
        السياسة المنشأة - Created policy
    """
    try:
        created_policy = policy_manager.add_policy(
            title=policy.title,
            content=policy.content,
            category=policy.category,
            tags=policy.tags
        )
        
        return {
            "detail": get_message("policy_uploaded", lang),
            "policy": created_policy
        }
    
    except Exception as e:
        logger.error(f"خطأ في إنشاء السياسة: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.post("/upload")
async def upload_policy_file(
    file: UploadFile = File(...),
    title: str = Query(..., description="عنوان السياسة - Policy title"),
    category: str = Query("general", description="فئة السياسة - Policy category"),
    tags: str = Query("", description="وسوم مفصولة بفواصل - Comma-separated tags"),
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    رفع ملف سياسة - Upload policy file (PDF, DOCX, TXT)
    
    Args:
        file: ملف السياسة - Policy file
        title: عنوان السياسة - Policy title
        category: فئة السياسة - Policy category
        tags: وسوم - Tags
        lang: اللغة - Language
    
    Returns:
        السياسة المنشأة - Created policy
    """
    try:
        # قراءة محتوى الملف - Read file content
        content = ""
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension == 'txt':
            content = (await file.read()).decode('utf-8')
        
        elif file_extension == 'pdf':
            pdf_bytes = await file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        
        elif file_extension == 'docx':
            docx_bytes = await file.read()
            doc = docx.Document(io.BytesIO(docx_bytes))
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
        
        else:
            raise HTTPException(
                status_code=400,
                detail="نوع الملف غير مدعوم. استخدم TXT أو PDF أو DOCX"
            )
        
        if not content.strip():
            raise HTTPException(
                status_code=422,
                detail="الملف فارغ أو لا يحتوي على نص"
            )
        
        # معالجة الوسوم - Process tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # إنشاء السياسة - Create policy
        created_policy = policy_manager.add_policy(
            title=title,
            content=content,
            category=category,
            tags=tag_list
        )
        
        return {
            "detail": get_message("policy_uploaded", lang),
            "policy": created_policy
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في رفع ملف السياسة: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.get("/")
async def get_all_policies(
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    الحصول على جميع السياسات - Get all policies
    
    Args:
        lang: اللغة - Language
    
    Returns:
        قائمة السياسات - List of policies
    """
    try:
        policies = policy_manager.get_all_policies()
        
        return {
            "detail": get_message("policies_retrieved", lang),
            "total": len(policies),
            "policies": policies
        }
    
    except Exception as e:
        logger.error(f"خطأ في الحصول على السياسات: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.get("/{policy_id}")
async def get_policy(
    policy_id: str,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    الحصول على سياسة محددة - Get specific policy
    
    Args:
        policy_id: معرف السياسة - Policy ID
        lang: اللغة - Language
    
    Returns:
        السياسة - Policy
    """
    try:
        policy = policy_manager.get_policy(policy_id)
        
        if not policy:
            raise HTTPException(
                status_code=404,
                detail=get_message("policy_not_found", lang)
            )
        
        return {
            "detail": get_message("success", lang),
            "policy": policy
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في الحصول على السياسة: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.put("/{policy_id}")
async def update_policy(
    policy_id: str,
    policy_update: PolicyUpdate,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    تحديث سياسة - Update policy
    
    Args:
        policy_id: معرف السياسة - Policy ID
        policy_update: بيانات التحديث - Update data
        lang: اللغة - Language
    
    Returns:
        السياسة المحدثة - Updated policy
    """
    try:
        updated_policy = policy_manager.update_policy(
            policy_id=policy_id,
            title=policy_update.title,
            content=policy_update.content,
            category=policy_update.category,
            tags=policy_update.tags
        )
        
        if not updated_policy:
            raise HTTPException(
                status_code=404,
                detail=get_message("policy_not_found", lang)
            )
        
        return {
            "detail": get_message("policy_updated", lang),
            "policy": updated_policy
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في تحديث السياسة: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: str,
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    حذف سياسة - Delete policy
    
    Args:
        policy_id: معرف السياسة - Policy ID
        lang: اللغة - Language
    
    Returns:
        رسالة النجاح - Success message
    """
    try:
        success = policy_manager.delete_policy(policy_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=get_message("policy_not_found", lang)
            )
        
        return {
            "detail": get_message("policy_deleted", lang)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في حذف السياسة: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.get("/search/query")
async def search_policies(
    query: Optional[str] = Query(None, description="نص البحث - Search query"),
    category: Optional[str] = Query(None, description="الفئة - Category"),
    tags: Optional[str] = Query(None, description="وسوم مفصولة بفواصل - Comma-separated tags"),
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    البحث في السياسات - Search policies
    
    Args:
        query: نص البحث - Search query
        category: الفئة - Category
        tags: الوسوم - Tags
        lang: اللغة - Language
    
    Returns:
        نتائج البحث - Search results
    """
    try:
        # معالجة الوسوم - Process tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # البحث - Search
        results = policy_manager.search_policies(
            query=query,
            category=category,
            tags=tag_list
        )
        
        return {
            "detail": get_message("policy_query_success", lang),
            "total_results": len(results),
            "results": results
        }
    
    except Exception as e:
        logger.error(f"خطأ في البحث عن السياسات: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )


@router.get("/statistics/summary")
async def get_policy_statistics(
    lang: str = Query("ar", description="اللغة - Language (ar/en)")
):
    """
    الحصول على إحصائيات السياسات - Get policy statistics
    
    Args:
        lang: اللغة - Language
    
    Returns:
        إحصائيات السياسات - Policy statistics
    """
    try:
        stats = policy_manager.get_statistics()
        
        return {
            "detail": get_message("success", lang),
            "statistics": stats
        }
    
    except Exception as e:
        logger.error(f"خطأ في الحصول على الإحصائيات: {e}")
        raise HTTPException(
            status_code=500,
            detail=get_message("error", lang) + f": {str(e)}"
        )

