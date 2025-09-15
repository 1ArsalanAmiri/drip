from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10               # تعداد آیتم‌ها در هر صفحه
    page_size_query_param = 'page_size'  # کاربر میتونه خودش سایز صفحه رو تعیین کنه
    max_page_size = 50         # حداکثر تعداد آیتم‌ها در هر صفحه