"""
نظام إدارة السياسات - Policy Management System
يوفر إمكانية تحميل وتخزين والبحث في سياسات الشركة
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

from app.config import POLICIES_DB_PATH, POLICIES_DIR


class PolicyManager:
    """مدير السياسات - Policy Manager"""
    
    def __init__(self):
        """تهيئة مدير السياسات - Initialize policy manager"""
        self.db_path = POLICIES_DB_PATH
        self.policies_dir = POLICIES_DIR
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """التأكد من وجود قاعدة بيانات السياسات - Ensure policy database exists"""
        if not self.db_path.exists():
            self._save_db([])
    
    def _load_db(self) -> List[Dict[str, Any]]:
        """تحميل قاعدة بيانات السياسات - Load policy database"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل قاعدة بيانات السياسات: {e}")
            return []
    
    def _save_db(self, policies: List[Dict[str, Any]]):
        """حفظ قاعدة بيانات السياسات - Save policy database"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(policies, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"خطأ في حفظ قاعدة بيانات السياسات: {e}")
            raise
    
    def add_policy(
        self,
        title: str,
        content: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        إضافة سياسة جديدة - Add new policy
        
        Args:
            title: عنوان السياسة - Policy title
            content: محتوى السياسة - Policy content
            category: فئة السياسة - Policy category
            tags: وسوم السياسة - Policy tags
            metadata: بيانات إضافية - Additional metadata
        
        Returns:
            السياسة المضافة - Added policy
        """
        policies = self._load_db()
        
        policy = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "category": category,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        policies.append(policy)
        self._save_db(policies)
        
        logger.info(f"تمت إضافة السياسة: {title}")
        return policy
    
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على سياسة محددة - Get specific policy
        
        Args:
            policy_id: معرف السياسة - Policy ID
        
        Returns:
            السياسة أو None - Policy or None
        """
        policies = self._load_db()
        for policy in policies:
            if policy["id"] == policy_id:
                return policy
        return None
    
    def get_all_policies(self) -> List[Dict[str, Any]]:
        """
        الحصول على جميع السياسات - Get all policies
        
        Returns:
            قائمة السياسات - List of policies
        """
        return self._load_db()
    
    def update_policy(
        self,
        policy_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        تحديث سياسة موجودة - Update existing policy
        
        Args:
            policy_id: معرف السياسة - Policy ID
            title: عنوان جديد - New title
            content: محتوى جديد - New content
            category: فئة جديدة - New category
            tags: وسوم جديدة - New tags
            metadata: بيانات إضافية جديدة - New metadata
        
        Returns:
            السياسة المحدثة أو None - Updated policy or None
        """
        policies = self._load_db()
        
        for i, policy in enumerate(policies):
            if policy["id"] == policy_id:
                if title is not None:
                    policy["title"] = title
                if content is not None:
                    policy["content"] = content
                if category is not None:
                    policy["category"] = category
                if tags is not None:
                    policy["tags"] = tags
                if metadata is not None:
                    policy["metadata"].update(metadata)
                
                policy["updated_at"] = datetime.now().isoformat()
                policies[i] = policy
                self._save_db(policies)
                
                logger.info(f"تم تحديث السياسة: {policy_id}")
                return policy
        
        return None
    
    def delete_policy(self, policy_id: str) -> bool:
        """
        حذف سياسة - Delete policy
        
        Args:
            policy_id: معرف السياسة - Policy ID
        
        Returns:
            True إذا تم الحذف، False إذا لم توجد السياسة
        """
        policies = self._load_db()
        initial_count = len(policies)
        
        policies = [p for p in policies if p["id"] != policy_id]
        
        if len(policies) < initial_count:
            self._save_db(policies)
            logger.info(f"تم حذف السياسة: {policy_id}")
            return True
        
        return False
    
    def search_policies(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        البحث في السياسات - Search policies
        
        Args:
            query: نص البحث - Search query
            category: فئة السياسة - Policy category
            tags: وسوم للبحث - Tags to search
        
        Returns:
            قائمة السياسات المطابقة - List of matching policies
        """
        policies = self._load_db()
        results = []
        
        for policy in policies:
            # تصفية حسب الفئة - Filter by category
            if category and policy.get("category") != category:
                continue
            
            # تصفية حسب الوسوم - Filter by tags
            if tags:
                policy_tags = set(policy.get("tags", []))
                search_tags = set(tags)
                if not search_tags.intersection(policy_tags):
                    continue
            
            # تصفية حسب نص البحث - Filter by query text
            if query:
                query_lower = query.lower()
                title_match = query_lower in policy.get("title", "").lower()
                content_match = query_lower in policy.get("content", "").lower()
                
                if not (title_match or content_match):
                    continue
            
            results.append(policy)
        
        logger.info(f"تم العثور على {len(results)} سياسة")
        return results
    
    def get_policy_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        الحصول على السياسات حسب الفئة - Get policies by category
        
        Args:
            category: فئة السياسة - Policy category
        
        Returns:
            قائمة السياسات - List of policies
        """
        return self.search_policies(category=category)
    
    def get_categories(self) -> List[str]:
        """
        الحصول على جميع الفئات - Get all categories
        
        Returns:
            قائمة الفئات - List of categories
        """
        policies = self._load_db()
        categories = set()
        for policy in policies:
            if "category" in policy:
                categories.add(policy["category"])
        return sorted(list(categories))
    
    def get_all_tags(self) -> List[str]:
        """
        الحصول على جميع الوسوم - Get all tags
        
        Returns:
            قائمة الوسوم - List of tags
        """
        policies = self._load_db()
        tags = set()
        for policy in policies:
            if "tags" in policy:
                tags.update(policy["tags"])
        return sorted(list(tags))
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات السياسات - Get policy statistics
        
        Returns:
            إحصائيات السياسات - Policy statistics
        """
        policies = self._load_db()
        
        return {
            "total_policies": len(policies),
            "categories": len(self.get_categories()),
            "tags": len(self.get_all_tags()),
            "categories_list": self.get_categories(),
            "tags_list": self.get_all_tags()
        }


# إنشاء نسخة عامة من مدير السياسات - Create global policy manager instance
policy_manager = PolicyManager()

