from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, analyzer, Completion, Keyword, Text, Integer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}
        
ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class ArticleType(DocType):
    # jobbole articles
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    comment_nums = Integer()
    fav_nums = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")

    class Meta:
        index = "jobbole"
        doc_type = "article"

class JobType(DocType):
    # lagou articles
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    salary=Keyword()
    city=Keyword()
    work_years=Keyword()
    degree=Keyword()
    type=Keyword()
    publish_time=Keyword()
    tags=Text(analyzer="ik_max_word")
    advantage=Keyword()
    description=Text(analyzer="ik_max_word")
    address=Keyword()
    company_url=Keyword()
    company_name=Keyword()

    class Meta:
        index = "lagou"
        doc_type = "job"

if __name__ == "__main__":
    JobType.init()