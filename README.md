Gerrit 命令行接口。

![](https://img.shields.io/pypi/pyversions/python-gerrit-cli.svg)
![](https://img.shields.io/pypi/v/python-gerrit-cli.svg)
![LICENSE](https://img.shields.io/github/license/pkemb/python-gerrit-cli.svg)
![](https://static.pepy.tech/badge/python-gerrit-cli)

## 安装

```shell
pip install python-gerrit-cli
```

## 使用方法

在使用之前需要先设置用户名和HTTP密码，这些信息存储在`~/gerrit.rc`。这一步只需要做一次。

```shell
gerritcli server add <name> <host> <username> <password>
```

可以添加多组信息（不同服务器，或同一服务器的不同用户），默认使用添加的第一组信息。`gerritcli server default <name>`修改默认值，也可以使用全局选项`-s <name>`指定服务器。

### 示例1：查看帮助信息

主命令和子命令都支持`-h`选项。

```shell
$ gerritcli -h
usage: gerritcli [-h] [-s SERVER] [--debug] command ...

positional arguments:
  command     command usage
    server    add/remove/list gerrit server info
    version   show gerrit server version
    project   project command
    account   account command help
    change    change command help
    group     group command
    patch     patch command help

optional arguments:
  -h, --help  show this help message and exit
  -s SERVER   specify gerrit server. If not specified, the default value is used
  --debug     enable debug

$ gerritcli change -h
usage: gerritcli change [-h] {search,get,create,delete} ...

positional arguments:
  {search,get,create,delete}
                        change command help
    search              Queries changes visible to the caller.
    get                 get change
    create              create change
    delete              delete change

optional arguments:
  -h, --help            show this help message and exit
```

### 示例2：查询服务器版本

```shell
gerritcli version
```

### 示例3：查询修改

查询自己还没有合并的修改。默认以表格的形式输出。关于搜索指令`is:open+is:owner`的更多信息，可以参考gerrit文档，[Searching Changes](https://gerrit-review.googlesource.com/Documentation/user-search.html#_search_operators)。

```shell
gerritcli change search 'is:open+is:owner'
```

### 示例4：指定输出格式

使用选项`--format`指定输出的格式，支持`table`、`csv`、`json`。例如查询分支`xxxxx`已合并的修改，并保存到文件。这样可以`Excel`等工具打开，进行二次分析。

```shell
gerritcli change search --format csv 'branch:xxxxx+is:merged' > merged_cl.csv
```

### 示例5：指定表头

`table`和`csv`格式默认只会打印`number`、`owner_name`、`subject`、`status`、`submitter_name`、`created`、`submitted`字段，`json`格式会打印所有字段。可以使用`--header`选项打印指定字段。例如只打印`number`和`subject`。支持的字段请参考`json`格式的输出。

```shell
gerritcli change search 'is:open+is:owner' --header 'number,subject'
```

### 示例6：列出所有的仓库

```shell
gerritcli project list
```

### 示例6：搜索活跃的账号

```shell
gerritcli account search 'is:active'
```

### 示例7：下载补丁

```shell
gerritcli patch <id>
```
