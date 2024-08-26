**파이썬으로 dxf파일 만들고 이미지,SVG파일로 변환(ft. ezdxf)**

토목 엔지니어링에서 빼놓을 수 없는 도구가 CAD다.  
파이썬으로 dxf파일을 핸들링 할 수 있는 모듈이 있어서 소개한다.  
ezdxf다. 아래 url참조

[https://ezdxf.readthedocs.io/en/stable/index.html](https://ezdxf.readthedocs.io/en/stable/index.html)

[https://github.com/mozman/ezdxf/tree/stable](https://github.com/mozman/ezdxf/tree/stable)

생각보다 기능이 많다.

파이썬에서 dxf파일을 만들고 그것을 저장할 수 있다. 그리고 다른 형식으로 변환도 가능하다.  
사용법은 의외로 간단하다.   
우선 아래와 같이 pip를 이용해서 설치한다.

| pip install ezdxf |
| :---- |

그리고 코드에서 아래와 같이 입력해서 ezdxf를 import한다.

| import ezdxf |
| :---- |

dxf를 만드는 건 간단하다.

doc을 정의 하고(dxf버전 정의) 난 다음 modelspace를 정의한 후 add\_로 요소들을 추가해주면 된다.  
코드를 보면 원은 중심점, 반지름을 지정하고 color를 지정했다.  
선은 시작점과 끝점을, 텍스트는 insert point와 높이, 색, 회전을 지정했다.  
doc을 saveas 메소드로 저장하면 파일로 생성된다.

```python
    doc \= ezdxf.new('R2010')
    msp \= doc.modelspace()
    msp.add\_circle((0, 0), 5, dxfattribs={'color': 1})  \# 빨간색으로 설정
    msp.add\_line((0, 0), (50,50), dxfattribs={'color': 1})
    msp.add\_text("Sample Text", dxfattribs={
        'insert': (0, 5),
        'height': 0.5,
        'color': 2,  \# 노란색
        'rotation': 30  \# 30도 회전
    })
    doc.saveas(filename)
```

필자는 claude 3.5 sonnet을 이용해서 몇가지 기능을 넣어봤다.  
필자가 필요한 기능은 GUI에서 dxf파일을 보여주는 기능인데, dxf파일을 GUI에서 직접 보여주는 모듈을 못찾았다.

dxf파일을 분석해서 요소별로 그래픽으로 구현하는 것도 가능하다.

그렇게 하는 것도 나쁘지 않은 방법인데 dxf형식을 GUI환경에서 지원하는 이미지(래스터,벡터)형식으로 변환하면 어떨까 하는 생각으로 만들어본 코드다.  
GUI환경까지는 만들지 않았고 일단 dxf를 PNG나 SVG로 만드는 것까지 해본 것이다.

svg형식은 text형식(XML)으로 되어있다. 그래서 dxf요소별로 해당 코드를 만드는 것으로 보인다. 이 코드에 없는 요소는 별도로 추가해줘야 하는 것으로 보인다. 현재 cicle,line,text가 포함되어 있다. arc와 dimension이 포함되면 어느정도 쓸만해질 것 같다.

그리고 dxf를 png로 변환하는 것은 matplotlib모듈을 이용해서 변환한다. matplotlib가 그래프 그리는 기능만 있는 줄 알았는데 다양한 기능이 있는 것으로 보인다.   

사용법은 다음과 같다. python으로 스크립트를 실행한다.

| python ezdxf2pngsvg.py |
| :---- |

그러면 아래와 같이 sample.dxf를 만들 것인지 아니면 기존 dxf파일을 읽을 것인지를 물어본다. 1을 선택하면 사용자가 지정한 dxf파일을 연다. 현재 디렉토리에 있는 파일만 가능하다. 2를 선택하면 sample.dxf를 생성한다.   
그런 다음 출력형식을 묻는다. png 또는 svg를 선택하면 된다.

| 현재 작업 디렉토리: C:\\Users\\PCuser\\OneDrive\\dev\\dxf1: 기존 DXF 파일 열기2: 샘플 DXF 파일 생성선택하세요 (1 또는 2): 2샘플 DXF 파일 'C:\\Users\\PCuser\\OneDrive\\dev\\dxf\\sample.dxf' 생성 완료출력 형식을 선택하세요 (png 또는 svg): svgSVG 파일 저장 완료: C:\\Users\\PCuser\\OneDrive\\dev\\dxf\\sample.svg변환 완료: 'sample.dxf' \-\> 'sample.svg' |
| :---- |

sample.dxf는 아래와 같이 원,선,텍스트 3개 요소로 이루어진 dxf파일이다.  
![image001](https://github.com/user-attachments/assets/a0f3bea8-3512-4934-b699-a024ae6f12af)

sample.svg파일은 아래와 같이 xml형식의 text파일이다.

| \<?xml version='1.0' encoding='utf-8'?\>\<svg width="3.3" height="1" viewBox="0.0 \-5.5 3.3 1" xmlns="[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)"\> \<circle cx="0.0" cy="-0.0" r="5.0" stroke="black" stroke-width="0.1%" fill="none" /\> \<line x1="0.0" y1="-0.0" x2="50.0" y2="-50.0" stroke="black" stroke-width="0.1%" /\> \<text x="0.0" y="-5.0" font-size="100.0%" fill="black" text-anchor="start" dominant-baseline="auto" transform="rotate(-30.0 0.0 \-5.0)"\>Sample Text\</text\> \</svg\> |
| :---- |

아래의 내용은 인공지능에게 이 코드를 설명해달라고 해서 받은 내용이다.

제공된 코드는 DXF (Drawing Exchange Format) 파일을 생성, 조작 및 PNG 또는 SVG 형식으로 변환하는 Python 스크립트입니다. DXF 파일 처리에는 ezdxf 라이브러리를 사용하고, 이미지 렌더링에는 matplotlib을 사용합니다. 스크립트는 각각 특정 작업을 담당하는 여러 함수로 구성됩니다.

**create\_sample\_dxf 함수**는 원, 선 및 텍스트 요소가 포함된 샘플 DXF 파일을 생성합니다. 이러한 요소에 대한 색상 및 회전과 같은 특정 속성을 설정하고 지정된 파일 이름으로 파일을 저장합니다.

**get\_entity\_color 함수**는 DXF 엔티티에서 색상 속성을 추출하고 이를 RGB 16진수 문자열로 변환합니다. 정수 기반 AutoCAD 색상 인덱스와 직접 RGB 튜플을 모두 처리하고, 색상이 지정되지 않았거나 오류가 발생하면 기본적으로 검정색을 사용합니다.

**create\_svg\_element 함수**는 DXF 엔티티를 해당 SVG 요소로 변환합니다. 선, 원, 호 및 텍스트를 지원하며, 위치, 크기, 색상 및 회전과 같은 속성을 SVG 형식에 맞게 조정합니다. 이 함수는 SVG 표현이 원래 DXF 엔티티의 시각적 속성을 유지하도록 합니다.

**calculate\_bounds 함수**는 DXF 문서의 모델 공간에 있는 모든 엔티티의 경계 상자를 계산합니다. 엔티티를 반복하여 최소 및 최대 좌표를 업데이트하여 도면의 전체 치수를 결정합니다.

**convert\_dxf 함수**는 변환 프로세스를 처리합니다. DXF 파일을 읽고 오류를 확인하고 도면 경계를 계산한 다음 matplotlib을 사용하여 PNG 이미지로 렌더링하거나 SVG 파일을 생성합니다. 최종 이미지 또는 SVG가 적절하게 확장되도록 출력 치수 및 해상도를 조정합니다.

**get\_user\_choice, get\_dxf\_file\_name 및 get\_output\_format 함수**는 사용자 입력을 처리하고, 기존 DXF 파일을 열지 아니면 샘플 파일을 생성할지를 선택하고, DXF 파일 이름을 지정하고, 출력 형식(PNG 또는 SVG)을 선택하도록 사용자에게 요청합니다.

마지막으로 스크립트의 기본 블록은 워크플로를 조정합니다. 현재 작업 디렉토리를 설정하고, 사용자에게 입력을 요청하고, DXF 파일을 생성하거나 열고, 변환을 수행합니다. 성공하면 사용자에게 변환 완료를 알리고, 그렇지 않으면 실패를 보고합니다.


[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOoAAADnCAYAAAAQCsqQAAAF3ElEQVR4Xu3bjW7bNhiG0dz/TWcgtgwuS8e2REp8yXOAArb+LCnfE2Vr8/UNTO+rXgDMR6gQQKgQQKgQQKgQQKgwka+vdpLtpcDlnkVaPF8DXOa3SIvf1wJTECrc6NWT9Md7WwHdvRtp8f6WQDefRFp8tjVw2qeRFp/vARx2JNLi2F7Ax45GWhzfE3jbmUiLc3sDL52NtDh/BOCpHpEWfY4C/KVXpEW/IwH/6xlp0fdoQPdIi/5HhI2NiLQYc1TY0KhIi3FHho2MjLQYe3TYwOhIi/GfAJwmVAggVAggVPjQFf9NWrv+EyHYHZEW93wqBLor0uK+T4Ygd0Za3PvpEODuSIv7zwAmNkOkxRxnAROaJdJinjOBicwUaTHX2cAEZou0mO+M4EYzRlrMeVZwg1kjLeY9M7jQzJEWc58dXGD2SIv5zxAGSoi0yDhL2JxQIYBQIYBQIYBQIYBQ2ULK/919Jvvs4Q3pkRb5VwC/WCHSYo2rgIZVIi3WuRJ4sFKkxVpXA9/rRVqsd0VsbcVIizWvii2tGmmx7pWxlZUjLda+OraweqTF+lfI0naItNjjKlnSLpEW+1wpBBMqBBAqBBAqBBAqBBAqBBAqBBAq09rp70lfcSeYkkj/5G4wHZH+zR1hKiJtc1eYhkifc2eYgkh/5+5wO5G+5g5xK5G+x13iNiJ9nzsFAYQKAYQKAYQKAYQKAYQKAYQKAYQKAYQKAYQKAYQKAYRKN/7t7jjuLF2IdCx3l9NEOp47zCkivYa7zGEivY47zSEivZa7DQGECgGECgGECgGECgGECgGECgGECgGECgGECgGECgGECgGECgGEujm/BZPBV2ljIs3hK7UpkWbx1dqQSPP4ikEAoUIAoUIAoUIAoUIAoUIAoUIAoUIAoUIAoUIAoUIAoUIAoUIAoUIAoUIAoQby+6T78RWHAEKFAEKFAEKFAEKFAEKFAEKFAEKFAEKFAEKFAEKFAEKFAEKFAEKFAEKFAEKFAEK9kF/45iiTcxGRcobpgQBChQBCPcmPtFzBlJ0kVK5gyk4qof78gVFM10GPcYqU0UzYQXWoYmUk0/WBxx9z6zCfLYceTNULrfhaUbaWQS+m6kEd2mN8r9bBSCbs++9AW8ta71uvYYStJ+y3p2JrXf0arrL1tNVPxTq+1vt6GVzB1P2nFWH9VG1tA1cwdQ9aIQqUGZi+yrMgny2HK2wzfe8+GVvb1O/haktOYB3bY6T1ulc+2RZGWXIK6xgf39frfvPudjDaspPYirOO9zev1sOVlp3GVqj1ekixzLQ+PjUfA22ta4ULM1tiWuvwWrE+LhcpaZaY2FZ8rVAhVeQUt36ErWMVKCuJmuY6zp9lrfVCZSUR01wH2Iqz3g5WEjHRdXyt963XsIopp7p+Mtbvf5a11NvBCm6f6DqqxyhbsdbbwQ5um/Q6xscg622evYdd3DL1dXCt13XEddCwk1umvg6ujrD1+kygZ/aFGdwywfUT8tWfM87uDzO4bYpbET4ua63/1Nn9YRZTTXKPOH/0Og7M4NZprn/E7RVXr+PALG6faJHCa7dOdc9Ai57HgplcPtmtJ2j9HvjT0DpaUb7r6H6woiEl9A6s9/EgTVQBgmVXcZMvVnbUbeoFBON0qeuOSO/4TLhL9LSLlV2cmnShwDUiSvMNgd0dLuCqeN75nHe2gWRTT7gA4V+HSrgioCs+A1JMWcORSI/sAymmm+6jwR3dDxJMNd1nYjuzL8zu4+keFcSo48IKPq5jRFAjjgkrub2QnpH2PBbMZKnJFiqrWmqyhcqqPp5sMcD1Pq5OqHC9ZarzDYSVLTPdQmVly0y3UFnZoekWBVxLcRDgcKgzPVVnOhcYwYRDgFOhepLBNaJL842CXXSZdMHAWN0KEyuME1eXbwjsqPvUjwpp1HEhwbDp7xVWr+NAsuEVlNCOxHZkH1jVZTW8E+zPNq+2g93cWoQo4T0qgQBChQBChQBChQBChQBChQBChQBChQD/AGoB+usz8OGEAAAAAElFTkSuQmCC>