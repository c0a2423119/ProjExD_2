import os
import random
import sys
import pygame as pg
import time

WIDTH, HEIGHT = 1100, 650
DELTA={
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0, +5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数:こうかとんrectまたは爆弾rect
    戻り値:判定タプル（横方向,縦方向）
    画面内:True/画面外:False
    """
    yoko=True
    tate=True
    if rct.left < 0 or rct.right > WIDTH:# 横方向のはみ出し
        yoko = False
    if rct.top < 0 or rct.bottom > HEIGHT:# 縦方向のはみ出し
        tate = False
    return yoko, tate


def game_over(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する
    引数:画面Surface
    戻り値:なし
    returnなし
    """
    go_sfc = pg.Surface((WIDTH, HEIGHT))  # 空のSurface
    go_sfc.fill((0, 0, 0))  # 黒い矩形
    go_sfc.set_alpha(200)  # 透明度
    font = pg.font.Font(None, 150)  # フォントオブジェクト
    go_txt = font.render("Game Over", True, (255, 255, 255))  # 白文字
    go_sfc.blit(go_txt, [WIDTH//2 - go_txt.get_width()//2, HEIGHT//2 - go_txt.get_height()//2])  # 中央に描画
    kc_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0)  # こうかとん画像
    go_sfc.blit(kc_img, [WIDTH//2 - go_txt.get_width()//2 - kc_img.get_width(), HEIGHT//2 - kc_img.get_height()//2])    # こうかとん画像を文字の左に描画
    go_sfc.blit(kc_img, [WIDTH//2 + go_txt.get_width()//2, HEIGHT//2 - kc_img.get_height()//2])  # こうかとん画像を文字の右に描画
    screen.blit(go_sfc, [0, 0])  # screenにblit
    pg.display.update()  # 画面更新
    time.sleep(5)  # 5秒間待機


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    中身：無限に拡大,加速するのはおかしいので,10段階程度の大きさを変えた爆弾Surfaceのリストと加速度のリストを準備する
    これらのリストのタプルbb_imgs, bb_accsを返す
    使い方：while文の前で呼び出して2つのリストを得る/while文の中でtmrの値に応じて,リストから適切な要素を選択する（一部掲載）：
    avx = vx*bb_accs[min(tmr//500, 9)]  このavxとavyをmove_ipメソッドに渡す
    bb_img = bb_imgs[min(tmr//500, 9)]
    """
    bb_imgs = []
    for r in range(1,11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)  # 色、座標、半径
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    bb_accs=[a for a in range(1,11)]
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルをキー,回転済みこうかとんSurfaceを値とした辞書を返す
    """
    kk_img0 = pg.image.load("fig/3.png")
    kk_imgs = {
        (0, -5): pg.transform.rotozoom(kk_img0,   -90, 0.9),   # 上
        (0, +5): pg.transform.rotozoom(kk_img0,  90, 0.9),   # 下
        (-5, 0): pg.transform.rotozoom(kk_img0,  0, 0.9),   # 左
        (+5, 0): pg.transform.rotozoom(kk_img0,    180, 0.9),   # 右
        (+5, -5): pg.transform.rotozoom(kk_img0,  45, 0.9),  # 右上
        (+5, +5): pg.transform.rotozoom(kk_img0,   -45, 0.9),  # 右下
        (-5, -5): pg.transform.rotozoom(kk_img0, 135, 0.9),  # 左上
        (-5, +5): pg.transform.rotozoom(kk_img0,  -135, 0.9),  # 左下
    }
    return kk_imgs



def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 色、座標、半径
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
        # 爆弾の初期化
    bb_imgs, bb_accs = init_bb_imgs()     # ← while前に1回だけ呼び出す
    bb_rct = bb_imgs[0].get_rect()        # ← 最初の爆弾サイズからrect作成
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5

    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(+5, 0)]  # 初期は右向き
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200


    
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 
        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾が重なったら
            game_over(screen) # ゲームオーバー画面を表示
            return

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]# 横方向の移動量を加算
                sum_mv[1] += mv[1]# 縦方向の移動量を加算
                
        #if key_lst[pg.K_UP]:
        #    sum_mv[1] -= 5
        #if key_lst[pg.K_DOWN]:
        #    sum_mv[1] += 5
        #f key_lst[pg.K_LEFT]:
        #    sum_mv[0] -= 5
        #if key_lst[pg.K_RIGHT]:
        #    sum_mv[0] += 5
        kk_rct.move_ip(sum_mv)
        # 移動処理
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        # 向きの切り替え
        if tuple(sum_mv) != (0, 0):  # 動いたときだけ画像を更新
            kk_img = kk_imgs.get(tuple(sum_mv), kk_img)

        screen.blit(kk_img, kk_rct)

        if check_bound(kk_rct)!=(True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)
        init_bb_imgs()  # 爆弾画像と加速度のリストを初期化
        bb_img = bb_imgs[min(tmr//500, 9)]  # tmrに応じた爆弾画像
        avx = vx*bb_accs[min(tmr//500, 9)]  # tmrに応じた横方向の速度
        avy = vy*bb_accs[min(tmr//500, 9)]  # tmrに応じた縦方向の速度
        bb_rct.move_ip(avx, avy)  # 爆弾の移動
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横方向にはみ出たら
            vx *= -1 # 横方向の速度を反転
        if not tate:  # 縦方向にはみ出たら
            vy *= -1  # 縦方向の速度を反転
        screen.blit(bb_img, bb_rct)  # 爆弾の描画
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
