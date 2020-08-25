# py_innodb_page_info

python tool for innodb page info
 
首先 要安装python

用法 ：

D:\> py py_innodb_page_info.py server_cost.ibd -v

- v 表示详细信息

如果报类似于KeyError: '0018'的错误，是因为8.0开始新增了很多种page type；请参照https://github.com/mysql/mysql-server/blob/8.0/storage/innobase/include/fil0fil.h 中constexpr page_type_t FIL_PAGE_相关的定义 ，找到错误的key的值对应的十进制编码（例如0018是16进制值，其十进制值是24，则对应constexpr page_type_t FIL_PAGE_TYPE_LOB_FIRST = 24;），将该key添加到include.py的innodb_page_type字典中。
