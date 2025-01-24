"""
google voice service
"""
import json

import openai
from pydub import AudioSegment

from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from voice.voice import Voice
import requests
from common import const
import datetime, random
from voice.audio_convert import any_to_mp3, any_to_sil

class OpenaiVoice(Voice):
    def __init__(self):
        openai.api_key = conf().get("open_ai_api_key_draw")

    def voiceToText(self, voice_file):
        reply = Reply()
        logger.info("[Openai] voice file name={}".format(voice_file))
        try:
            logger.info("[Openai] load arm from file:{}".format(voice_file))
            mp3Path = "/tmp/voice.mp3"
            self.armToMp3(voice_file, mp3Path)
            file = open(mp3Path, "rb")
            api_base = "https://api.openai.com/v1"
            url = f'{api_base}/audio/transcriptions'
            headers = {
                'Authorization': 'Bearer ' + conf().get("open_ai_api_key_draw"),
                # 'Content-Type': 'multipart/form-data' # 加了会报错，不知道什么原因
            }
            files = {
                "file": file,
            }
            data = {
                "model": "whisper-1",
            }
            logger.info("[Openai] voice file name={}".format(voice_file))
            response = requests.post(url, headers=headers, files=files, data=data)
            response_data = response.json()
            logger.info("[Openai] response={}".format(response_data))
            text = response_data['text']
            reply.type = ReplyType.TEXT
            reply.content = text
            logger.info("[Openai] voiceToText text={} voice file name={}".format(text, voice_file))
        except Exception as e:
            logger.error("[Openai] voiceToText error={}".format(text, response_data))
            reply.type = ReplyType.ERROR
            reply.content = "我暂时还无法听清您的语音，请稍后再试吧~"
        finally:
            logger.info("reply: {}".format(reply))
            return reply


    def textToVoice(self, text):
        try:
            api_base = conf().get("open_ai_api_base") or "https://api.openai.com/v1"
            url = f'{api_base}/audio/speech'
            headers = {
                'Authorization': 'Bearer ' + conf().get("open_ai_api_key_draw"),
                'Content-Type': 'application/json'
            }
            data = {
                'model': conf().get("text_to_voice_model") or const.TTS_1,
                'input': text,
                'voice': conf().get("tts_voice_id") or "alloy"
            }
            response = requests.post(url, headers=headers, json=data)
            file_name = "tmp/" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(0, 1000)) + ".mp3"
            logger.debug(f"[OPENAI] text_to_Voice file_name={file_name}, input={text}")
            with open(file_name, 'wb') as f:
                f.write(response.content)
            logger.info(f"[OPENAI] text_to_Voice success")
            reply = Reply(ReplyType.VOICE, file_name)
        except Exception as e:
            logger.error(e)
            reply = Reply(ReplyType.ERROR, "遇到了一点小问题，请稍后再问我吧")
        return reply


    def armToMp3(self, armPath, mp3Path):
        try:
            # 读取AMR文件
            sound = AudioSegment.from_file(armPath, format="amr")

            # 导出为MP3文件
            sound.export(mp3Path, format="mp3")
            logger.info(f"[OPENAI] armToMp3 success, path={mp3Path}")
        except Exception as e:
            logger.error(e)
