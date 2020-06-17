import pathlib
import pdf2image

import cv2
import numpy as np
import math

from PIL import Image, ImageFilter

# PDFから一旦画像を生成する
def makePdf2Image(pdf):
    pdf_file = pathlib.Path('in_pdf/' + pdf)
    img_dir = pathlib.Path('out_img')
    if not img_dir.exists():
        img_dir.mkdir()

    # PDFを画像に変換
    base = pdf_file.stem
    images = pdf2image.convert_from_path(pdf_file, grayscale=True, size=1800)
    for index, image in enumerate(images):
        image.save(img_dir/pathlib.Path(base + '-{}.png'.format(index + 1)), 'png')
        # 以前のスクリプトの反省を活かして途中経過表示
        print('Save:' + base + '-{}.png'.format(index + 1))

    return base, images

# 指定した画像に影をかける
def makeShadow(image, iterations, border, offset, backgroundColour, shadowColour):
    # image: base image to give a drop shadow
    # iterations: number of times to apply the blur filter to the shadow
    # border: border to give the image to leave space for the shadow
    # offset: offset of the shadow as [x,y]
    # backgroundCOlour: colour of the background
    # shadowColour: colour of the drop shadow
    
    #Calculate the size of the shadow's image
    fullWidth  = image.size[0] + abs(offset[0]) + 2*border
    fullHeight = image.size[1] + abs(offset[1]) + 2*border
    
    #Create the shadow's image. Match the parent image's mode.
    shadow = Image.new("L", (fullWidth, fullHeight), backgroundColour)
    print('\rSaving...make Shadow Image',end='')

    # Place the shadow, with the required offset
    shadowLeft = border + max(offset[0], 0) #if <0, push the rest of the image right
    shadowTop  = border + max(offset[1], 0) #if <0, push the rest of the image down
    #Paste in the constant colour
    shadow.paste(shadowColour, 
                [shadowLeft, shadowTop,
                 shadowLeft + image.size[0],
                 shadowTop  + image.size[1] ])
    
    # Apply the BLUR filter repeatedly
    for i in range(iterations):
        shadow = shadow.filter(ImageFilter.BLUR)
        print('\rSaving...ImageFilter.BLUR ' + str(i) + ' / ' + str(iterations),end='')

    # ここだけ追加。元のままだと影色と背景色が上手くなじまなかったのでshadowの色みをいじった。ココが遅い。
    if shadow.mode != "RGB":
        shadow=shadow.convert("RGB")
    w,h = shadow.size
    print('\rSaving...Set color...\033[K',end='')
    for x in range(w):
        for y in range(h):
            r,g,b=shadow.getpixel((x,y))
            # ここで色味いじり中、白色と設定したい背景色の差分を引くので注意
            shadow.putpixel((x,y), (r-77, g-40, b-14))
        print('\rSaving...Set color... ' + str(x) + ' / ' + str(w),end='')

    # Paste the original image on top of the shadow 
    imgLeft = border - min(offset[0], 0) #if the shadow offset was <0, push right
    imgTop  = border - min(offset[1], 0) #if the shadow offset was <0, push down
    shadow.paste(image, (imgLeft, imgTop))

    return shadow

# makeShadowを全ての画像にかけたいだけの関数
def makeShadowList(base, images):    
    img_dir = pathlib.Path('out_img/shadow')
    if not img_dir.exists():
        img_dir.mkdir()
    for index, image in enumerate(images):
        print('\rSaving...',end='')
        image = Image.open('out_img/' + base + '-{}.png'.format(index + 1))
        img = makeShadow(image,iterations=50, border=50, backgroundColour=0xafeeee, shadowColour=0x0006e, offset=(-10,15))
        img.save('out_img/shadow/' + base + '_shadow-{}.png'.format(index + 1))
        print('\rSave:' + base + '_shadow-{}.png\033[K'.format(index + 1))

# 1次元リストを2次元リストに変換する
def convert_1d_to_2d(l, cols):
    return [l[i:i + cols] for i in range(0, len(l), cols)]

# 2次元リストの画像から
def concat_tile(im_list_2d):
    return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

def makeTileImage(base, images):
    imgs = []
    for index, image in enumerate(images):
        img = cv2.imread('out_img/shadow/' + base + '_shadow-{}.png'.format(index + 1))
        imgs.append(img)

    result = convert_1d_to_2d(imgs, 6)
    im_tile = concat_tile(result)
    cv2.imwrite('out_img/result/tile.png', im_tile)
    print('Save:tile.png')

def main():
    base, images = makePdf2Image('in_pdf.pdf')
    makeShadowList(base, images)
    makeTileImage(base, images)

if __name__ == '__main__':
    main()