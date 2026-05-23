import requests
from pathlib import Path
import time
import warnings
import sys
from collections import Counter
import datetime
import io
import base64

# matplotlib 和 numpy 在 generate_graph 内部懒导入，加快冷启动速度

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

DAN = ['士', '杰', '豪', '圣', '天', '魂']
PT_BASE = {301: 6, 302: 7, 303: 10, 401: 14, 402: 16, 403: 18, 501: 20, 502: 30, 503: 45}

def get_level_color(level):
    major = level // 100 % 100
    minor = level % 10
    colors = [
        '#00FF00',
        '#80FF00',
        '#FFFF00',
        '#FFC000',
        '#FF8000',
        '#FF4000',
        '#FF0000',
        '#C00080',
        '#8000C0',
        '#0080FF'
    ]
    if major == 3:
        idx = minor - 1
    elif major == 4:
        idx = minor + 2
    elif major == 5:
        idx = minor + 5
    elif major == 7:
        idx = 9
    else:
        idx = 0
    return colors[idx] if idx < len(colors) else colors[0]

maid_to_ma = {16: '王南', 12: '玉南', 9: '金南',
               15: '王东', 11: '玉东', 8: '金东',
               26: '王南', 24: '玉南', 22: '金南',
               25: '王东', 23: '玉东', 21: '金东'}

def level_dan(level):
    return f"{DAN[level // 100 % 100 - 2]}{level % 100}"

def level_pt_base(level):
    return 5000 if level // 100 % 100 >= 6 else PT_BASE[level % 1000] * 100

def get_rank(player_list, target_account_id):
    sorted_list = sorted(player_list, key=lambda x: x['score'], reverse=True)
    sorted_ids = [player['accountId'] for player in sorted_list]
    return sorted_ids.index(target_account_id) + 1

FONT_PATH = Path(__file__).parent / "NotoSansSC-Regular.otf"

def _setup_cjk_font():
    import matplotlib.font_manager as fm
    import matplotlib.pyplot as plt
    if FONT_PATH.exists():
        fm.fontManager.addfont(str(FONT_PATH))
        font_prop = fm.FontProperties(fname=str(FONT_PATH))
        font_name = font_prop.get_name()
        plt.rcParams['font.sans-serif'] = [font_name]
    else:
        try:
            system_fonts = [f.name for f in fm.fontManager.ttflist]
            font_candidates = [
                'Microsoft YaHei', 'SimHei', 'WenQuanYi Micro Hei',
                'Noto Sans CJK SC', 'Noto Sans SC', 'Noto Sans CJK JP',
                'PingFang SC', 'Meiryo', 'DejaVu Sans'
            ]
            for font in font_candidates:
                if font in system_fonts:
                    plt.rcParams['font.sans-serif'] = [font]
                    return
        except Exception:
            pass
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']


def generate_graph(player_name: str, mode_arg: str = "4p", left: int = 0, right: int = 10000, top: int = 10000):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    import numpy as np
    _setup_cjk_font()
    plt.rcParams['axes.unicode_minus'] = False
    
    if mode_arg == "3p":
        API_BASE = "https://5-data.amae-koromo.com/api/v2/pl3/"
        MODE = "26,24,22,25,23,21"
        COLOR = {26: 'r', 25: 'r', 24: 'g', 23: 'g', 22: 'y', 21: 'y'}
        MODE_NAME = "三麻"
        pre_level = 20301
    else:
        API_BASE = "https://5-data.amae-koromo.com/api/v2/pl4/"
        MODE = "16,15,12,11,9,8"
        COLOR = {16: 'r', 15: 'r', 12: 'g', 11: 'g', 9: 'y', 8: 'y'}
        MODE_NAME = "四麻"
        pre_level = 10301

    try:
        search_result = requests.get(f"{API_BASE}search_player/{player_name}", verify=False).json()
    except Exception as e:
        return None, []
    if not search_result:
        return None, []

    player = search_result[0]
    pid = player['id']
    start = player['latest_timestamp']
    games = []

    for i in range(100):
        url = f"{API_BASE}player_records/{pid}/{start}999/1262304000000?limit=500&mode={MODE}&descending=true&tag="
        data = requests.get(url, verify=False).json()
        length = len(data)
        if length == 0:
            break
        start = data[-1]['startTime'] - 1
        games += data
        if length < 500:
            break
        time.sleep(0.01)

    if top == 10000:
        max_base = 0
        seen_levels = set()
        for game in games:
            for data in game['players']:
                if data['accountId'] == pid:
                    level = data['level']
                    if level not in seen_levels:
                        seen_levels.add(level)
                        base = level_pt_base(level)
                        if base > max_base:
                            max_base = base
        top = max_base
        bottom = -max_base
    else:
        bottom = -top

    fig, ax = plt.subplots(figsize=(16, 10), facecolor='#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    ax.spines['bottom'].set_color('#888888')
    ax.spines['top'].set_color('#888888')
    ax.spines['left'].set_color('#888888')
    ax.spines['right'].set_color('#888888')
    ax.tick_params(colors='#cccccc')
    ax.xaxis.label.set_color('#cccccc')
    ax.yaxis.label.set_color('#cccccc')
    ax.title.set_color('#ffffff')

    pre_pt, pt, base = 600, 600, 600
    hist = []
    temp_hist = []
    level_changes = {}
    pt_segments = []
    current_segment_x = []
    current_segment_y = []
    current_segment_level = pre_level

    for i, game in enumerate(games[::-1]):
        for data in game['players']:
            if data['accountId'] == pid:
                level = data['level']
                if pre_level != level:
                    if current_segment_x:
                        pt_segments.append((current_segment_x.copy(), current_segment_y.copy(), level_dan(current_segment_level), current_segment_level))
                    if temp_hist:
                        hist.append(temp_hist)
                    temp_hist = []
                    current_segment_x = []
                    current_segment_y = []
                    base = level_pt_base(level)
                    pt = pre_pt = base
                    current_segment_level = level
                    level_changes[i] = level
                pt += data['gradingScore'] * 5 if level // 100 % 100 >= 7 else data['gradingScore']
                rank = get_rank(game['players'], pid)
                dt1 = datetime.datetime.fromtimestamp(game['startTime'])
                dt2 = datetime.datetime.fromtimestamp(game['endTime'])
                ma = game['modeId']
                gdata = (i, dt1, dt2, maid_to_ma[ma], level_dan(pre_level), level_dan(level), rank, pre_pt, pt)
                temp_hist.append(gdata)
                if left <= i <= right:
                    current_segment_x.append(i + 1)
                    current_segment_y.append(pt)
                pre_level, pre_pt = level, pt
                break

    if current_segment_x:
        pt_segments.append((current_segment_x, current_segment_y, level_dan(current_segment_level), current_segment_level))

    if temp_hist:
        hist.append(temp_hist)

    bar_width = 0.8
    for seg_x, seg_y, dan_str, seg_level in pt_segments:
        filtered_x = [x for x in seg_x if left <= x <= right]
        seg_base = level_pt_base(seg_level)
        filtered_y = []
        for x in filtered_x:
            idx = seg_x.index(x)
            filtered_y.append(seg_y[idx] - seg_base)
        if filtered_x:
            color = get_level_color(seg_level)
            ax.bar(filtered_x, filtered_y, width=bar_width, color=color, edgecolor=color, alpha=0.8)
            mid_x = (filtered_x[0] + filtered_x[-1]) / 2
            ax.text(mid_x, bottom + 50, dan_str, fontsize=14, ha='center', color=color)

    for idx, dan_level in level_changes.items():
        if left <= idx <= right:
            change_base = level_pt_base(dan_level)
            ax.axvline(x=idx + 1, ymin=0.5 - change_base/(top-bottom), ymax=0.5 + change_base/(top-bottom), color='#888888', linestyle=':', linewidth=1)

    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)

    ax.set_title(f'雀魂PT推移图[{MODE_NAME}]({player_name})', fontsize=24)
    ax.set_xlabel('对局数', fontsize=16)
    ax.set_ylabel('PT (相对base)', fontsize=16)
    ax.set_xlim(left, min(right, len(games)))
    ax.set_ylim(bottom - 50, top + 50)
    ax.grid(True, alpha=0.3, axis='y', color='#444444')
    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150)
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()

    history_table = []
    for g in hist:
        a = np.array(g)
        n = len(a)
        counter_mas = Counter(a[:, 3])
        ranks = a[:, 6]
        counter_ranks = Counter(ranks)
        ro = [counter_ranks[i] for i in (1, 2, 3, 4)]
        pts = np.concatenate([a[:, 7], [a[:, 8][-1]]])
        s0 = ', '.join(f'{k}{v}' for k, v in counter_mas.items())
        period = (a[:, 2][-1].date() - a[:, 1][0].date()).days + 1
        start_date = a[:, 1][0].strftime("%Y/%m/%d")
        end_date = a[:, 2][-1].strftime("%Y/%m/%d")
        level = a[:, 4][-1]
        history_table.append({
            'level': level,
            'start_date': start_date,
            'end_date': end_date,
            'days': period,
            'games': n,
            'rank1': ro[0],
            'rank2': ro[1],
            'rank3': ro[2],
            'rank4': ro[3],
            'avg_rank': f"{np.mean(ranks):.3f}",
            'max_pt': int(pts.max()),
            'min_pt': int(pts.min()),
            'mode_types': s0
        })

    return img_base64, history_table

if __name__ == "__main__":
    import sys
    PLAYER_NAME = sys.argv[1] if len(sys.argv) > 1 else ""
    MODE_ARG = sys.argv[2] if len(sys.argv) > 2 else "4p"
    LEFT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    RIGHT = int(sys.argv[4]) if len(sys.argv) > 4 else 10000
    TOP = int(sys.argv[5]) if len(sys.argv) > 5 else 10000

    img_base64, history_table = generate_graph(PLAYER_NAME, MODE_ARG, LEFT, RIGHT, TOP)
    
    if img_base64 is None:
        print("未找到玩家或获取数据失败！")
        sys.exit(1)
    
    print(f"\n=== 雀魂段位战历史[{MODE_ARG}]({PLAYER_NAME}) ===\n")
    print(f"{'段位':<8} {'开始日期':<12} {'结束日期':<12} {'天数':<6} {'对局数':<8} {'1位':<4} {'2位':<4} {'3位':<4} {'4位':<4} {'平均排名':<10} {'最高PT':<8} {'最低PT':<8} {'场次类型':<20}")
    print("="*150)
    for row in history_table:
        print(f"{row['level']:<8} {row['start_date']:<12} {row['end_date']:<12} {row['days']:<6} {row['games']:<8} {row['rank1']:<4} {row['rank2']:<4} {row['rank3']:<4} {row['rank4']:<4} {row['avg_rank']:<10} {row['max_pt']:<8} {row['min_pt']:<8} {row['mode_types']:<20}")
    
    with open("mahjong_pt_graph.png", "wb") as f:
        import base64
        f.write(base64.b64decode(img_base64))
    print(f"\n图表已保存为 mahjong_pt_graph.png")
