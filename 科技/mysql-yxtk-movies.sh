#!/bin/sh
source ./commParams.sh;
index=news;
type=funny;
sql='select *, \"news\" as _index, \"funny\" as _type, id as _id, concat(\"news_funny_\",id) as sid from 3rd_funny';
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
bin=${DIR}/../../bin
lib=${DIR}/../../lib
echo '
{
    "type" : "jdbc",
    "jdbc" : {
        "url" : "'$jdbcUrl'",
        "user" : "'$jdbcUserName'",
        "password" : "'$jdbcPassword'",
        "sql" : "'$sql'" ,
        "elasticsearch" : {
            "cluster":"'$esCluster'",
            "host" : "'$esHost'",
            "port" : '$esPort'
        },
        "elasticsearch.autodiscover" : "true",
        "index":"'$index'",
        "type":"'$type'"
    }
}
' | java \
    -cp "${lib}/*" \
    -Dlog4j.configurationFile=${bin}/log4j2.xml \
    org.xbib.tools.Runner \
    org.xbib.tools.JDBCImporter
