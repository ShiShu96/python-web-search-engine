from flask import Blueprint, request, jsonify
from flask import render_template
from datetime import datetime

from app.models import ArticleType, JobType
main=Blueprint('main', __name__)

from elasticsearch import Elasticsearch
client=Elasticsearch(hosts=['127.0.0.1'])


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/suggest')
def suggest():
    key_words=request.args.get("s","")
    datas=[]
    if key_words:
        s1=ArticleType.search()
        s2=JobType.search()
        
        s1 = s1.suggest('article_suggestions', key_words, completion={
                "field":"suggest", "fuzzy":{
                    "fuzziness":2
                },
                "size": 3
            })
        s2=s2.suggest('job_suggestions', key_words, completion={
            "field":"suggest", "fuzzy":{
                    "fuzziness":2
            },
            "size": 3
        })
        s1=s1.execute_suggest()
        s2=s2.execute_suggest()
        for r in s1.article_suggestions[0].options:
            source=r._source
            datas.append(source["title"])
        for r in s2.job_suggestions[0].options:
            source=r._source
            datas.append(source["title"])
    return jsonify(datas) 

@main.route("/search")
def search():
    key_words=request.args.get("s","")
    start_time = datetime.now()
    article_response=client.search(
        index="jobbole",
        body={
            "query":{
                "multi_match":{
                    "query":key_words,
                    "fields":["tags","title","content"]
                }
            },
            "highlight": {
                "pre_tags": ['<span class="key">'],
                "post_tags": ['</span>'],
                "fields": {
                    "title": {},
                    "content": {},
                }
            }
        }
    )
    job_response=client.search(
        index="lagou",
        body={
            "query":{
                "multi_match":{
                    "query":key_words,
                    "fields":["tags","title","description"]
                }
            },
            "highlight": {
                "pre_tags": ['<span class="key">'],
                "post_tags": ['</span>'],
                "fields": {
                    "title": {},
                    "description": {},
                }
            }
        }
    )
    end_time = datetime.now()
    last_seconds = (end_time-start_time).total_seconds()

    article_hits=[]
    job_hits=[]
    for hit in article_response["hits"]["hits"]:

        hit_dict = {}
        if hit.get("highlight") and "title" in hit["highlight"]:
            hit_dict["title"] = "".join(hit["highlight"]["title"])
        else:
            hit_dict["title"] = hit["_source"]["title"]
        if hit.get("highlight") and  "content" in hit["highlight"]:
            hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
        else:
            hit_dict["content"] = hit["_source"]["content"][:500]

        hit_dict["url"] = hit["_source"]["url"]
        hit_dict["score"] = hit["_score"]

        article_hits.append(hit_dict)

    for hit in job_response["hits"]["hits"]:
        hit_dict = {}
        if hit.get("highlight") and  "title" in hit["highlight"]:
            hit_dict["title"] = "".join(hit["highlight"]["title"])
        else:
            hit_dict["title"] = hit["_source"]["title"]
        if hit.get("highlight") and  "description" in hit["highlight"]:
            hit_dict["description"] = "".join(hit["highlight"]["description"])[:200]
        else:
            hit_dict["description"] = hit["_source"]["description"][:200]

        hit_dict["url"] = hit["_source"]["url"]
        hit_dict["score"] = hit["_score"]

        job_hits.append(hit_dict)

    total_hits=len(article_hits)+len(job_hits)

    return render_template("search.html",
                            key_words=key_words,
                            last_seconds=last_seconds,
                            total_hits=total_hits,
                            article_hits=article_hits,
                            job_hits=job_hits)
    

    
