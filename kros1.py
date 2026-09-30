import time
import random

print('Loading Files... (49KB/1024KB)')
time.sleep(1)
print('Loading Files... (325KB/1024KB)')
time.sleep(1)
print('Loading Files... (1024KB/1024KB)')
time.sleep(3)
print('Loading Forge Files... (144KB/14000KB)')
time.sleep(1)
print('Loading Forge Files... (1460KB/14000KB)')
time.sleep(1)
print('Loading Forge Files... (7102KB/14000KB)')
time.sleep(1)
print('Loading Forge Files... (14000KB/14000KB)')
time.sleep(3)
print('Loading KrOS... (17KB/19250KB)')
time.sleep(1)
print('Loading KrOS... (1560KB/19250KB)')
time.sleep(1)
print('Loading KrOS... (7368KB/19250KB)')
time.sleep(5)
print('Welcome to KrOS!')
time.sleep(3)

# ============ ZhiMaSu Game Module ============
class ZhiMaSuCat:
    def __init__(self):
        self.fish_eaten = 0
        self.inflated = False
        self.boom_left = 0
        self.alive = True

    def status(self):
        pct = min(100, int(self.fish_eaten / 320 * 100))
        bar = "[" + "#" * (pct // 5) + "-" * (20 - pct // 5) + "]"
        return f"Fish: {self.fish_eaten}/320 {bar} {pct}%"

    def feed(self, amount=1):
        if not self.alive:
            print("  >> The cat is gone. Nothing to feed.")
            return
        if self.inflated:
            print("  >> ZhiMaSu is ALREADY inflated! Stay back!")
            return
        self.fish_eaten += amount
        print(f"  >> Fed {amount} raw cod. {self.status()}")
        if self.fish_eaten >= 320:
            self._inflate()

    def _inflate(self):
        self.inflated = True
        self.boom_left = 6
        print()
        print("  ╔════════════════════════════════════╗")
        print("  ║   ZhiMaSu has become ROUND!        ║")
        print("  ║   Imminent chain explosion!        ║")
        print("  ╚════════════════════════════════════╝")
        print()

    def tick(self):
        if not self.inflated or not self.alive:
            return
        if self.boom_left > 0:
            power = random.randint(12, 17)
            print(f"  💥 BOOM #{6 - self.boom_left + 1}! (Power {power}, Radius {power}m)")
            self.boom_left -= 1
            if self.boom_left == 0:
                self._kick()

    def _kick(self):
        self.alive = False
        print()
        print("  " + "━" * 39)
        print("  >>> KICK <<<")
        print("  >>> Because you overfed ZhiMaSu, and you don't have Hibiki's")
        print("      strength, you were squeezed out of MC and the game crashed!")
        print("  " + "━" * 39)
        print()

    def auto_demo(self):
        print("  >> Auto-demo mode: feeding 320 raw cod...")
        print()
        while self.fish_eaten < 320:
            self.feed(1)
            time.sleep(0.01)
        print()
        for _ in range(6):
            self.tick()
            time.sleep(0.8)


def zhimasu_game():
    """ZhiMaSu Game - returns to KrOS main menu when done"""
    print()
    print("   ╔════════════════════════════════════════╗")
    print("   ║     Oh! ZhiMaSu Cat - Simulator        ║")
    print("   ║     A deep-blue, very fat cat         ║")
    print("   ╚════════════════════════════════════════╝")
    print()

    cat = ZhiMaSuCat()

    while True:
        print("  Commands: feed <n> | status | auto | help | back")
        try:
            cmd = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n  >> Returned to KrOS.")
            return

        if cmd == "back" or cmd == "exit" or cmd == "quit":
            print("  >> Returning to KrOS main menu...")
            time.sleep(1)
            return  # ← 关键：返回 KrOS 主界面
        elif cmd == "help":
            print("  Commands:")
            print("    feed <n>   - Feed n raw cod (default 1)")
            print("    status     - Show current status")
            print("    auto       - Run automated demo (320 fish)")
            print("    back       - Return to KrOS main menu")
        elif cmd == "status":
            print(f"  >> {cat.status()}")
            if cat.inflated:
                print("  >> ⚠️  INFLATED - chain explosion in progress!")
        elif cmd == "auto":
            cat.auto_demo()
            print("\n  >> Game over. Returning to KrOS...")
            time.sleep(2)
            return  # ← 爆炸演示完后也返回主界面
        elif cmd.startswith("feed"):
            parts = cmd.split()
            if len(parts) > 1 and parts[1].isdigit():
                cat.feed(int(parts[1]))
            else:
                cat.feed(1)
        elif cmd == "":
            pass
        else:
            print("  >> Unknown command. Type 'help'.")


# ============ KrOS Main Loop ============
while True:
    a = input('''
Which file do you want to open?
This Computer
White Board
Colorful Eggs
Internet Explorer
Shutdown
CMD
Intel(R) HD Graphics Seetings
Zhimasu Game
> ''')

    if (a == 'This Computer'):
        print('''
                      Intel Core i5-2410
                      NVIDIA GeForce GTS 450
                      4GB DDR3
                      240GB HDD
                      KrOS 0.9.9 Pro
                      Internet:False
                      ''')
        time.sleep(6)
        continue

    elif (a == 'White Board') :
        print('The whiteboard is temporarily unavailable.')
        time.sleep(3)
        continue

    elif (a == 'Zhimasu Game'):
        zhimasu_game()  # ← 调用游戏函数，结束后自动回到这里
        continue

    elif (a == 'Colorful Eggs') :
        print('''
                      KrOS crashes due to Forge library crash
                      It has crashed now
                      Please reinstall the new Forge
                      library URL: https://www.bluesheep.com/en-us/forgeURL/Forge-en-us-1.0.0.0335/
              ''')
        time.sleep(5)
        break

    elif a==("Internet Explorer"):
        print("The Internet is False!")
        time.sleep(5)
        continue

    elif a==("CMD"):
        while True:
            b=input("CMD> ")
            if b==("KrOComputer_d"):
                print("""
                     Intel Core i5-2410
                      NVIDIA GeForce GTS 450
                      4GB DDR3
                      240GB HDD
                      KrOS 0.9.9 Pro
                      Internet:False
                     """)
                time.sleep(3)
                continue
            elif b==("KrInternetw"):
                print("""
                      TP-LINK-40N6
                      HUAWEI-34N
                      iPhone(4)
                      CMCC-8kP2
                     """)
                time.sleep(3)
                continue
            elif b==("KrPresForge"):
                print("Forge Version:1.0.0.0336Pre")
                time.sleep(3)
                continue
            elif b==("KrPresForge_d"):
                print("""
                      KrOS crashes due to Forge library crash
                      It has crashed now
                      Please reinstall the new Forge
                      library URL: https://www.bluesheep.com/en-us/forgeURL/Forge-en-us-1.0.0.0335/
                     """)
                time.sleep(3)
                break
            elif b==("Exit"):
                break
            elif b==("KrIntelHDs"):
                print("Intel (R) HD Graphics Seeting Loading...  1024KB/8192KB")
                time.sleep(3)
                print("Intel (R) HD Graphics Seeting Loading...  4108KB/8192KB")
                time.sleep(3)
                while True:
                    d=input("""
Intel HD Graphics Seeting
Which setting do you want?
    3D Seetings
    resolution
    Video
    Exit
                          """)
                    if d==("3D"):
                        print("The 3D option is temporarily unavailable")
                        time.sleep(3)
                        continue
                    elif d==("resolution"):
                        e=input("What resolution do you want to tune to?Current resolution: 1920 * 1080")
                        if e==("1600 * 900"):
                            print("Loading...")
                            time.sleep(5)
                            print("OK!")
                            continue
                        elif e==("1920 * 991"):
                            print("Loading...")
                            time.sleep(1)
                            print("OK!")
                            continue
                    if d==("Video"):
                        f=input("Which refresh rate do you want?")
                        rd=("120 Hz")
                        if f==("60 Hz") and f!=rd:
                            print("Loading")
                            time.sleep(3)
                            print("OK")
                            rd=f
                            continue
                        elif f==("120 Hz") and f!=rd:
                            print("Loading")
                            time.sleep(1)
                            print("OK")
                            rd=f
                            continue
                        elif f==("240 Hz") and f!=rd:
                            print("Loading")
                            time.sleep(2)
                            print("OK")
                            rd=f
                            continue
                        elif f==rd:
                            print("It's already this refresh rate")
                            time.sleep(2)
                            continue
                    elif d==("Exit"):
                        break
            elif b==("KrBugsCreacil"):
                print("""
These are all bugs and changelogs fixed by KrOS
0.9.8
    KrOS 0.3.6 Enternint
    KrOS Security Patch [2024#7]
0.9.9
    KrOS Security Patch [2024#8]
    KrOS Python's Originds
    KrOS Security Patch [2024#9]
    Intel HD Graphics KB-R150KH835M2
    KrOS Python's for Intel HD Graphics Seetings App
    KrOS Forge Lib(0.5.3)
1.0.0
    KrOS Security Patch [2024#10]
    KrOS Python's Interander
1.0.1
    KrOS Python's for Zhimasu Game App
    KrOS Security Patch[2026#9]
    KrOS Forge Lib(0.7.7)
                        """)
            else:
                print("They are NOT True")
                time.sleep(3)
                continue

    elif a==("Intel(R) HD Graphics Seetings"):
        print("Intel (R) HD Graphics Seeting Loading...  1024KB/8192KB")
        time.sleep(3)
        print("Intel (R) HD Graphics Seeting Loading...  4108KB/8192KB")
        time.sleep(3)
        while True:
            d=input("""
Intel HD Graphics Seeting
Which setting do you want?
    3D Seetings
    resolution
    Video
    Exit
                  """)
            if d==("3D"):
                print("The 3D option is temporarily unavailable")
                time.sleep(3)
                continue
            elif d==("resolution"):
                e=input("What resolution do you want to tune to?Current resolution: 1920 * 1080")
                if e==("1600 * 900"):
                    print("Loading...")
                    time.sleep(5)
                    print("OK!")
                    continue
                elif e==("1920 * 991"):
                    print("Loading...")
                    time.sleep(1)
                    print("OK!")
                    continue
            if d==("Video"):
                f=input("Which refresh rate do you want?")
                rd=("120 Hz")
                if f==("60 Hz") and f!=rd:
                    print("Loading")
                    time.sleep(3)
                    print("OK")
                    rd=f
                    continue
                elif f==("120 Hz") and f!=rd:
                    print("Loading")
                    time.sleep(1)
                    print("OK")
                    rd=f
                    continue
                elif f==("240 Hz") and f!=rd:
                    print("Loading")
                    time.sleep(2)
                    print("OK")
                    rd=f
                    continue
                elif f==rd:
                    print("It's already this refresh rate")
                    time.sleep(2)
                    continue
            elif d==("Exit"):
                break

    elif a==("Shutdown"):
        c=input("Shutdown? (Yes/No) > ")
        if c==("Yes"):
            print("Loading Shutdown Forge and KrOS")
            time.sleep(3)
            print("See you again!")
            time.sleep(2)
            print("Closing KrOS...")
            time.sleep(18)
            print("bye!")
            time.sleep(5)
            break
        if c==("no"):
            continue
