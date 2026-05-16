import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import warnings
import sys
import numpy as np
from collections import Counter
import datetime
import io
import base64

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

maid_to_ma = {16: '4王南', 12: '4玉南', 9: '4金南',
               15: '4王东', 11: '4玉东', 8: '4金东',
               26: '3王南', 24: '3玉南', 22: '3金南',
               25: '3王东', 23: '3玉东', 21: '3金东'}

def level_dan(level):
    return f"{DAN[level // 100 % 100 - 2]}{level % 100}"

def level_pt_base(level):
    return 5000 if level // 100 % 100 >= 6 else PT_BASE[level % 1000] * 100

def get_rank(player_list, target_account_id):
    sorted_list = sorted(player_list, key=lambda x: x['score'], reverse=True)
    sorted_ids = [player['accountId'] for player in sorted_list]
    return sorted_ids.index(target_account_id) + 1

def generate_graph(player_name: str, mode_arg: str = "4p", left: int = 0, right: int = 10000, top: int = 10000):
    if mode_arg == "3p":
        API_BASE = "https://5-data.amae-koromo.com/api/v2/pl3/"
        MODE = "26,24,22,25,23,21"
        COLOR = {26: 'r', 25: 'r', 24: 'g', 23: 'g', 22: 'y', 21: 'y'}
        MODE_NAME = "3麻"
        pre_level = 20301
    else:
        API_BASE = "https://5-data.amae-koromo.com/api/v2/pl4/"
        MODE = "16,15,12,11,9,8"
        COLOR = {16: 'r', 15: 'r', 12: 'g', 11: 'g', 9: 'y', 8: 'y'}
        MODE_NAME = "4麻"
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
        top = max_base * 2

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'MingLiU']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(facecolor='w', figsize=(16, 10))

    if left == 0:
        plt.text(3, 100, f'杰\n1', fontsize=15)

    pre_pt, pt, base = 600, 600, 600
    hist = []
    temp_hist = []

    for i, game in enumerate(games[::-1]):
        for data in game['players']:
            if data['accountId'] == pid:
                level = data['level']
                if pre_level != level:
                    if temp_hist:
                        hist.append(temp_hist)
                    temp_hist = []
                    base = level_pt_base(level)
                    pt = pre_pt = base
                    if left <= i <= right:
                        s = level_dan(level)
                        plt.text(i+3, 100, f'{s[0]}\n{s[1:]}', fontsize=15)
                        plt.vlines(i, 0, max(level_pt_base(level), level_pt_base(pre_level))*2, color='k')
                pt += data['gradingScore'] * 5 if level // 100 % 100 >= 7 else data['gradingScore']
                rank = get_rank(game['players'], pid)
                dt1 = datetime.datetime.fromtimestamp(game['startTime'])
                dt2 = datetime.datetime.fromtimestamp(game['endTime'])
                ma = game['modeId']
                gdata = (i, dt1, dt2, maid_to_ma[ma], level_dan(pre_level), level_dan(level), rank, pre_pt, pt)
                temp_hist.append(gdata)
                if left <= i <= right:
                    level_color = get_level_color(level)
                    plt.plot([i, i+1], [pre_pt, pt], color='k', lw=1.5)
                    plt.fill_between([i, i+1], [pre_pt, pt], color=level_color, alpha=0.3)
                    plt.plot([i, i+1], [base, base], color='k', lw=1.5)
                    plt.plot([i, i+1], [base*2, base*2], color='k', lw=1.5)
                pre_level, pre_pt = level, pt
                break

    if temp_hist:
        hist.append(temp_hist)

    plt.title(f'雀魂PT推移图[{MODE_NAME}]({player_name})', fontsize=30)
    plt.xlabel('对局数', fontsize=20)
    plt.ylabel('PT', fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks([i*1000 for i in range(11)], fontsize=20)
    plt.xlim([left, min(right, len(games))])
    plt.ylim([0, top+100])
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
