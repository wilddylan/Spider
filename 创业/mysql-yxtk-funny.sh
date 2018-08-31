#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
bin=${DIR}/../../bin
lib=${DIR}/../../lib

echo '
{
    "type" : "jdbc",
    "jdbc" : {
                "url" : "jdbc:mysql://yxtkmysqldb.mysql.rds.aliyuncs.com:3306/yxtk-resource",
        "user" : "resource",
        "password" : "resource@1234",        "sql" : "select *, \"news\" as _index, \"funny\" as _type, id as _id, concat(\"news_funny_\",id) as sid from 3rd_funny" ,
        "elasticsearch" : {
            "cluster":"production_v3.1",
            "host" : "10.171.207.171",
            "port" : 9300
        },
	"elasticsearch.autodiscover" : "true",
        "index":"news",
        "type":"funny"
    }
}
' | java \
    -cp "${lib}/*" \
    -Dlog4j.configurationFile=${bin}/log4j2.xml \
    org.xbib.tools.Runner \
    org.xbib.tools.JDBCImporter
