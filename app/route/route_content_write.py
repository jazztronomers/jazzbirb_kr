from flask import request, jsonify, Blueprint, current_app
from jazzbirb_kr.app.models.models_content_read import ContentReader
from jazzbirb_kr.app.models.models_content_write import ContentWriter
from jazzbirb_kr.app.models.models_user import User
from jazzbirb_kr.app.util.app_logger import logger
from jazzbirb_kr.app.constant import *
from flask import request, redirect, url_for, session
from datetime import datetime
import json

app_content_writer = Blueprint('content_write', __name__, url_prefix='/')

@app_content_writer.route('/submitPost', methods=['POST'])
def submit_post():
    if request.method == 'POST' and session.get('loggedin'):

        start = datetime.now()

        user_id = session.get("user_id")
        title = request.form.get('title')
        content = request.form.get('content')
        location = request.form.get('location', [])
        camera = request.form.get('camera', [])
        lens = request.form.get('lens', [])
        items = [{"item_id": k, "item_value":v} for k,v in request.files.items()]



        category = request.form.get('category')
        option = request.form.get('option')

        # SERVER SIDE VALIDATION
        if category in CONST_SUPER_CATEGORY.keys() and session.get('user_lv', 'c') != 's':
            logger.warn('category power overwhelming')
            category = CONST_GENERAL_CATEGORY.keys[0]


        ret = ContentWriter(user_id=user_id).write_post(title=title,
                                                  content=content,
                                                  items=items,
                                                  location=location,
                                                  camera=camera,
                                                  lens=lens,
                                                  category=category,
                                                  option=option)

        return jsonify({"result": True, "message": "%s" % (datetime.now() - start), "post_id": ret.get("post_id")})

    else:
        return jsonify({'result': False, 'code': 400, 'message': 'Bad request'})


@app_content_writer.route('/submitCommentPost', methods=['POST'])
def submit_comment_post():
    if request.method == 'POST' and session.get('loggedin'):

        start = datetime.now()

        user_id = session.get("user_id")
        post_id = request.json.get("post_id")
        comment_content=request.json.get("content")
        ContentWriter(user_id=user_id).write_comment_post(post_id=post_id,
                                                          content=comment_content,
                                                          user_id=user_id)

        return jsonify({"result": True, "message": "%s" % (datetime.now() - start)})

    else:
        return jsonify({'result': False, 'code': 400, 'message': 'Bad request'})

@app_content_writer.route('/likePost', methods=['POST'])
def like_post():
    if request.method == 'POST' and session.get('loggedin'):

        start = datetime.now()

        user_id = session.get("user_id")
        post_id = request.json.get("post_id")
        ret = ContentWriter(user_id=user_id).like_post(post_id=post_id,
                                                 user_id=user_id)




        return jsonify(ret)

    else:
        return jsonify({'result': False, 'code': 400, 'message': 'Bad request'})


# POST:
# ITEM:
@app_content_writer.route('/meta/set', methods=['POST'])
def set_meta():
    if request.method == 'POST' and session.get('loggedin'):


        user_id = session.get("user_id")
        post_id = request.json.get("post_id")
        item_id = request.json.get("item_id")
        meta = request.json.get("meta")
        species = meta.get('species')



        if species == '':
            meta['species'] = None
        elif species in CONST_BIRD_DICT_KEY_SPECIES.keys():
            meta['species']= CONST_BIRD_DICT_KEY_SPECIES.get(species).get("bid")

        if meta.get('x') == '':
            meta['x'] = None


        if meta.get('y') == '':
            meta['y'] = None
        if meta.get('camera') == '':
            meta['camera'] = None
        if meta.get('lens') == '':
            meta['lens'] = None




        ret_set_meta = ContentWriter(user_id=user_id).set_meta(user_id=user_id, meta=meta, item_id=item_id, post_id=post_id)
        if meta['x']:
            ret_set_location = User(session.get("user_id")).set_location({"x": meta.get('x'), "y": meta.get('y')})

        logger.info('%s...%s%s' %(ret_set_location, meta.get('y'), meta.get('x')))

        return jsonify(ret_set_meta)

    else:
        return jsonify({'result': False, 'code': 400, 'message': 'Bad request'})