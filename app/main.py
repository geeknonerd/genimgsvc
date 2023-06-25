import os
from typing import Union

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import Response
from imaginepy import Imagine, Style, Ratio
from pydantic import BaseModel, validator

AUTH_TOKEN = os.getenv('TOKEN', '')
app = FastAPI()

ALL_STYLE = list(Style.__members__.keys())
ALL_RATIO = list(Ratio.__members__.keys())


class Args(BaseModel):
    prompt: str
    style: Union[str, None] = 'ANIME_V2'
    ratio: Union[str, None] = 'RATIO_16X9'
    negative: Union[str, None] = None
    priority: Union[str, None] = None
    steps: Union[str, None] = None
    high_res_results: Union[str, None] = None
    seed: Union[str, None] = None
    cfg: float = 9.5

    @validator('style')
    def validate_style(cls, s):
        if s not in ALL_STYLE:
            raise ValueError(f'style err: {ALL_STYLE}')
        return Style[s]

    @validator('ratio')
    def validate_ratio(cls, r):
        if r not in ALL_RATIO:
            raise ValueError(f'ratio err: {ALL_RATIO}')
        return Ratio[r]


def sdprem(args: Args, upscale: bool = False) -> Union[bytes, None]:
    imagine = Imagine(style=Style.ANIME_V2)
    img_data = imagine.sdprem(**args.dict())
    if img_data is None:
        print('An error occurred while generating the image.')
        return
    if not upscale:
        return img_data

    img_data = imagine.upscale(image=img_data)
    if img_data is None:
        print('An error occurred while upscaling the image.')
        return
    return img_data


def auth_by_token(token: str):
    if not AUTH_TOKEN:
        return
    if token == AUTH_TOKEN:
        return
    raise HTTPException(status_code=403)


@app.post('/imagine/sdprem')
def imagine_sdprem(args: Args, upscale: bool = False, token: str = Header(None)):
    auth_by_token(token)
    image_bytes: bytes = sdprem(args, upscale)
    if not image_bytes:
        raise HTTPException(status_code=503)
    return Response(content=image_bytes, media_type='image/png')


if __name__ == '__main__':
    try:
        with open('example.jpeg', mode='wb') as img_file:
            img_file.write(imagine_sdprem(
                Args(prompt='Woman sitting on a table, looking at the sky, seen from behind')))
    except Exception as e:
        print(f'An error occurred while writing the image to file: {e}')
