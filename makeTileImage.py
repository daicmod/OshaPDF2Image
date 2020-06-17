from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from PIL import Image, ImageFilter

# 画像をテクスチャにして貼る
def img2tex(img_path):  
    img = Image.open(img_path)
    img = img.convert('RGBA')
    img_data = img.tobytes()

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(
        GL_TEXTURE_2D,  #target
        0,  #level
        GL_RGBA,  #internalformat
        img.size[0], img.size[1],  #width, height
        0,  #border
        GL_RGBA,  #format
        GL_UNSIGNED_BYTE,  #type
        img_data  #pixels
    )
    return tex

def display():
    m = (
        [-1.0,  1.0, 0.0],
        [ 1.0,  1.0, 0.0],
        [ 1.0, -1.0, 0.0],
        [-1.0, -1.0, 0.0])
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glBindTexture(GL_TEXTURE_2D, img2tex('out_img/result/transopencv_concat_tile.png'))
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glBegin(GL_POLYGON)
    glTexCoord2d(0.0, 0.0); glVertex3dv(m[0])
    glTexCoord2d(1.0, 0.0); glVertex3dv(m[1])
    glTexCoord2d(1.0, 1.0); glVertex3dv(m[2])
    glTexCoord2d(0.0, 1.0); glVertex3dv(m[3])
    glEnd()

    glFlush()

def resizeA(w, h):
    glViewport(0, 0, w, h)
    glLoadIdentity()
    gluPerspective(
    1.0,  #fovy
    1.0,  #aspect
    0.0, 10.0  #zNear, zFar
    )
    
    glRotated(40.0, 0.0, 0.0, 1.0)
    
    # 画角を編集したい場合はここをいじります
    gluLookAt(
     -7.0,  -11.0,  16.0, #eye
     0.4,  0.4,  0.0,  #center
     0.0,  1.0,  0.0   #up
    )

# 画像を保存する
def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        glReadBuffer(GL_FRONT)
        buf = glReadPixels(
          0 ,0,  #x, y
          1000, 1000,  #width, height
          GL_RGBA,  #format
          GL_UNSIGNED_BYTE,  #type
        )
        img = Image.frombuffer('RGBA', (1000, 1000), buf)
        img.save('tmp.png')

glutInit()
glutInitWindowSize(1000, 1000)
glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH)
glutCreateWindow(b'TileImage.')

glutDisplayFunc(display)
glutReshapeFunc(resizeA)
glutMouseFunc(mouse)

glClearColor(0.0, 0.0, 0.5, 0.0)

glEnable(GL_TEXTURE_2D)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_BLEND)
glEnable(GL_LINE_SMOOTH)
glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

glutMainLoop()
