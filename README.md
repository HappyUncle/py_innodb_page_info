# py_innodb_page_info

用法 ：

```bash
$ python py_innodb_page_info.py -h
Get InnoDB Page Info
Usage: python py_innodb_page_info.py [OPTIONS] tablespace_file
The following options may be given as the first argument:
  -h        help
  -o output put the result to file
  -t number thread to anayle the tablespace file
  -v        verbose mode

$ python py_innodb_page_info.py test.ibd -v
```

如果报类似于KeyError: '0018'的错误，是因为8.0开始新增了很多种page type；请参照https://github.com/mysql/mysql-server/blob/8.0/storage/innobase/include/fil0fil.h 中constexpr page_type_t FIL_PAGE_相关的定义 ，找到错误的key的值对应的十进制编码（例如0018是16进制值，其十进制值是24，则对应constexpr page_type_t FIL_PAGE_TYPE_LOB_FIRST = 24;），将该key添加到innodb_page_type字典中。
