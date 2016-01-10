# movement app backend

Dev environment:

yum install python-pip python-psycopg2
pip install --upgrade pip
pip install requests
pip install pyYAML
pip install BeautifulSoup
pip install Elasticsearch


vim /opt/bernie/config.yml

elasticsearch:
    host: localhost

postgresql:
    dbname: movement
    dbuser: bernie
    dbpass: sanders
    host: localhost
    port: 5432

youtube:
    api_key: __key_goes_here__
