import ezdxf
import matplotlib.pyplot as plt
from ezdxf import recover
from ezdxf.addons.drawing import Frontend, RenderContext
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import os
import sys
import xml.etree.ElementTree as ET
import math

def create_sample_dxf(filename):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    msp.add_circle((0, 0), 5, dxfattribs={'color': 1})  # 색상을 빨간색으로 설정
    msp.add_line((0, 0), (50,50), dxfattribs={'color': 1})
    msp.add_text("Sample Text", dxfattribs={
        'insert': (0, 5),
        'height': 0.5,
        'color': 2,  # 노란색
        'rotation': 30  # 30도 회전
    })
    doc.saveas(filename)
    print(f"샘플 DXF 파일 '{filename}' 생성 완료")

def get_entity_color(entity):
    try:
        if hasattr(entity, 'dxf'):
            color = entity.dxf.color
            if isinstance(color, int):
                # AutoCAD 색상 인덱스를 RGB로 변환
                rgb = ezdxf.colors.aci_to_true_color(color)
                return f"#{rgb:06x}"  # RGB를 16진수 문자열로 변환
            elif isinstance(color, tuple) and len(color) == 3:
                return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        return 'black'  # 기본 색상
    except Exception:
        return 'black'  # 오류 발생 시 기본 색상 반환

def create_svg_element(entity, svg, min_x, min_y, max_x, max_y):
    color = get_entity_color(entity)
    stroke_width = '0.1%'  # 선 두께를 SVG 뷰포트의 0.1%로 설정
    if isinstance(entity, ezdxf.entities.Line):
        ET.SubElement(svg, 'line', {
            'x1': str(entity.dxf.start[0]),
            'y1': str(-entity.dxf.start[1]),  # SVG에서 Y축이 반대
            'x2': str(entity.dxf.end[0]),
            'y2': str(-entity.dxf.end[1]),
            'stroke': color,
            'stroke-width': stroke_width
        })
    elif isinstance(entity, ezdxf.entities.Circle):
        ET.SubElement(svg, 'circle', {
            'cx': str(entity.dxf.center[0]),
            'cy': str(-entity.dxf.center[1]),
            'r': str(entity.dxf.radius),
            'stroke': color,
            'stroke-width': stroke_width,
            'fill': 'none'
        })
    elif isinstance(entity, ezdxf.entities.Arc):
        center = entity.dxf.center
        radius = entity.dxf.radius
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        path = f"M {center[0] + radius * math.cos(math.radians(start_angle))} {-center[1] - radius * math.sin(math.radians(start_angle))} " \
               f"A {radius} {radius} 0 0 0 {center[0] + radius * math.cos(math.radians(end_angle))} {-center[1] - radius * math.sin(math.radians(end_angle))}"
        ET.SubElement(svg, 'path', {
            'd': path,
            'stroke': color,
            'stroke-width': stroke_width,
            'fill': 'none'
        })
    elif isinstance(entity, ezdxf.entities.Text):
        # 텍스트 크기를 SVG 뷰포트에 맞게 조정
        font_size = entity.dxf.height / (max_y - min_y) * 100
        # 회전 각도 적용
        rotation = entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0
        # 텍스트 정렬 처리
        alignment = entity.dxf.insert
        text_anchor = 'start'
        if hasattr(entity.dxf, 'halign'):
            if entity.dxf.halign > 0:
                text_anchor = 'middle' if entity.dxf.halign == 1 else 'end'
        baseline = 'auto'
        if hasattr(entity.dxf, 'valign'):
            if entity.dxf.valign > 0:
                baseline = 'middle' if entity.dxf.valign == 1 else 'hanging'
        
        text_element = ET.SubElement(svg, 'text', {
            'x': str(alignment[0]),
            'y': str(-alignment[1]),
            'font-size': f"{font_size}%",
            'fill': color,
            'text-anchor': text_anchor,
            'dominant-baseline': baseline,
            'transform': f"rotate({-rotation} {alignment[0]} {-alignment[1]})"
        })
        text_element.text = entity.dxf.text

def calculate_bounds(msp):
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    for entity in msp:
        if isinstance(entity, ezdxf.entities.Text):
            insert = entity.dxf.insert
            min_x = min(min_x, insert[0])
            min_y = min(min_y, insert[1])
            # 텍스트의 너비와 높이 정보가 없으므로 대략적인 크기 추정
            max_x = max(max_x, insert[0] + entity.dxf.height * len(entity.dxf.text) * 0.6)
            max_y = max(max_y, insert[1] + entity.dxf.height)
        elif hasattr(entity, 'get_bbox'):
            bbox = entity.get_bbox()
            if bbox:
                min_x = min(min_x, bbox.extmin[0])
                min_y = min(min_y, bbox.extmin[1])
                max_x = max(max_x, bbox.extmax[0])
                max_y = max(max_y, bbox.extmax[1])
    
    # 경계가 유효하지 않은 경우 기본값 설정
    if min_x == float('inf') or min_y == float('inf') or max_x == float('-inf') or max_y == float('-inf'):
        min_x, min_y, max_x, max_y = -10, -10, 10, 10

    return min_x, min_y, max_x, max_y

def convert_dxf(dxf_file, output_file, output_format):
    try:
        # DXF 파일 불러오기
        doc, auditor = recover.readfile(dxf_file)
        if auditor.has_errors:
            print(f"DXF 파일 '{dxf_file}'에 오류가 있습니다:")
            for error in auditor.errors:
                print(f" - {error}")
            return False

        # 도면의 경계 계산
        msp = doc.modelspace()
        min_x, min_y, max_x, max_y = calculate_bounds(msp)

        width = max(max_x - min_x, 1)  # 최소 너비 1
        height = max(max_y - min_y, 1)  # 최소 높이 1

        if output_format == 'png':
            # 이미지 크기 제한
            max_size = 65000  # 픽셀
            scale = min(max_size / width, max_size / height)
            fig_width = int(width * scale)
            fig_height = int(height * scale)

            # DPI 계산 (최대 300으로 제한)
            dpi = min(300, fig_width / width)

            # matplotlib 설정
            fig = plt.figure(figsize=(fig_width/dpi, fig_height/dpi), dpi=dpi)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_axis_off()

            # 렌더링 컨텍스트와 백엔드 설정
            ctx = RenderContext(doc)
            ctx.set_current_layout(doc.modelspace())
            ctx.bounds = (min_x, min_y, max_x, max_y)
            out = MatplotlibBackend(ax)

            # 엔티티 렌더링
            Frontend(ctx, out).draw_layout(msp, finalize=True)

            # PNG 파일로 저장
            plt.savefig(output_file, dpi=dpi, bbox_inches='tight', pad_inches=0, facecolor='white')
            plt.close(fig)  # 명시적으로 figure 객체 닫기
            print(f"이미지 크기: {fig_width}x{fig_height} 픽셀, DPI: {dpi:.2f}")

        elif output_format == 'svg':
            # SVG 생성
            svg = ET.Element('svg', {
                'width': f"{width}",
                'height': f"{height}",
                'viewBox': f"{min_x} {-max_y} {width} {height}",
                'xmlns': "http://www.w3.org/2000/svg"
            })

            for entity in msp:
                create_svg_element(entity, svg, min_x, min_y, max_x, max_y)

            # SVG 파일로 저장
            tree = ET.ElementTree(svg)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            print(f"SVG 파일 저장 완료: {output_file}")

        return True
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False

def get_user_choice():
    while True:
        choice = input("1: 기존 DXF 파일 열기\n2: 샘플 DXF 파일 생성\n선택하세요 (1 또는 2): ").strip()
        if choice in ['1', '2']:
            return choice
        print("잘못된 선택입니다. 1 또는 2를 입력하세요.")

def get_dxf_file_name():
    file_name = input("DXF 파일의 이름을 입력하세요 (확장자 포함): ").strip()
    if not file_name.lower().endswith('.dxf'):
        file_name += '.dxf'
    return file_name

def get_output_format():
    while True:
        choice = input("출력 형식을 선택하세요 (png 또는 svg): ").strip().lower()
        if choice in ['png', 'svg']:
            return choice
        print("잘못된 선택입니다. 'png' 또는 'svg'를 입력하세요.")

if __name__ == "__main__":
    current_dir = os.getcwd()
    print(f"현재 작업 디렉토리: {current_dir}")

    choice = get_user_choice()

    if choice == '1':
        dxf_file = get_dxf_file_name()
        full_path = os.path.join(current_dir, dxf_file)
        if not os.path.exists(full_path):
            print(f"오류: '{dxf_file}' 파일이 현재 디렉토리에 없습니다.")
            sys.exit(1)
    else:
        dxf_file = "sample.dxf"
        full_path = os.path.join(current_dir, dxf_file)
        create_sample_dxf(full_path)

    output_format = get_output_format()
    output_file = os.path.splitext(full_path)[0] + f".{output_format}"

    # DXF를 선택한 형식으로 변환
    if convert_dxf(full_path, output_file, output_format):
        print(f"변환 완료: '{dxf_file}' -> '{os.path.basename(output_file)}'")
    else:
        print("변환 실패")