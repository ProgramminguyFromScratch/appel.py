class appel_physics:
    def __init__(self, map_data, map_rotations, LSX):
        self.MAP = map_data
        self.MAP_R = map_rotations
        self.MASK = ("", "", "5555   1h", "5555   1h", "5005   1h", "5000   1h", "5050   xh", "5..5   3h", "       2", ".00.   3", "5555   1h", "    02 4", "111100 2", "5055   1h", "5000   1", "****   5", "100100 2", "5555   1h", "5555   1h", "    04 4", "5555   1h", "5555   1h", "    00 2", "    80 6", "    81 6", "       5", "       5", "        ", "        ", "        ", "        ", "    06 4", "    82 4h", "5555   1h", "0660   6", "0660    ", "0660    ", "0660    ", "0660    ", "0660    ", "        ", "        ", "5665   6h", "5555    h", "5555   6h", "    08 4", "0600   6", "0600   ", "0600   ", "0600   ", "5775   6h", "5775   6h", "", "", "", "", "", "", "    09 4", "    84 4", "    60 7", "    10 4", "    11 4", "       5", "", "", "", "", "5555   1h", "    12 5", "    00 5", "    00 2", "6600   6", "100181 6", "....   3h", "    13 4", "    00 5", ".      3h", "   .   3h", "1111   2h", "1111   5h", "5115   2h", "5111   2h", ".00.   3h", "111100 2", "****00 5", "5555   1h")
        self.PSZ = [0, 17, 13, 17, 13]
        self.LSX = LSX
        self.toverlap = 0
        self.last_tick_keys = ""
        self.direction = 90
        
        self.mask_char = 0
        self.overlap = 0
        self.RESOLVE = [0, 0, 1, 0, -1, -1, 0, 1, 0, -1, -1, 1, -1, -1, 1, 1, 1]
        
    def get_block_at(self, x, y):
        try:
            idx = int(x // 60) + int(y // 60) * self.LSX
            tile = self.MAP[idx]
            mask = self.MASK[int(tile)]

            if x % 60 < 30:
                mid = 1 if y % 60 < 30 else 2
            else:
                mid = 0 if y % 60 < 30 else 3
            return mask[((mid - int(self.MAP_R[idx])) % 4)]
        except:
            return "0"
            
    def is_solid_at(self, x, y, dir):
        self.mask_char = self.get_block_at(x, y, )
        self.fix_mask()
        if self.mask_char <= 4:
            return

        if dir == 1:
            temp = x % 30
        elif dir > 0:
            temp = 30 - (y % 30)
        elif dir == -1:
            temp = 30 - (x % 30)
        else:
            temp = y % 30

        if temp > self.overlap:
            self.overlap = temp
            
    def touching_wall_dx(self, player_state, dir):
        if player_state["player_state"] == "spin" or player_state["is_falling"] < 3:
            return
        
        self.overlap = 0
        self.is_solid_at(player_state["PLAYER_X"] + (dir * -30), player_state["PLAYER_Y"] + 8, dir)
        self.is_solid_at(player_state["PLAYER_X"] + (dir * -30), player_state["PLAYER_Y"] - 8, dir)
        if self.overlap == 0:
            self.is_solid_at(player_state["PLAYER_X"] + (dir * 4), player_state["PLAYER_Y"] + 4, dir)
            if self.overlap > 0:
                self.overlap = 0
                self.is_solid_at(player_state["PLAYER_X"] + (dir * 4), player_state["PLAYER_Y"] - 4, dir)
                if self.overlap > 0 and abs(player_state["PLAYER_SX"]) > 3:
                    if (not dir == player_state["flipped"]) or player_state["player_state"] == "wall spin":
                        player_state["player_state"] = "spin"
                        self.set_flipped(player_state, dir)
                    player_state["player_wall"] = str(dir)

    def full_overlap(self, x, y, dir, dxy2):
        tx = x
        ty = y
        self.toverlap = 0
        for _ in range(4):
            self.overlap = 0
            self.is_solid_at(tx, ty, dir)
            if dir % 2 == 0:
                self.is_solid_at(tx + dxy2, ty, dir)
            else:
                self.is_solid_at(tx, ty + dxy2, dir)
            if self.overlap == 0:
                return
            self.overlap += 0.01
            self.toverlap += self.overlap
            if dir > 0:
                if dir == 1:
                    tx -= self.overlap
                else:
                    ty += self.overlap
            else:
                if dir == -1:
                    tx += self.overlap
                else:
                    ty -= self.overlap

    def set_flipped_safe(self, player_state, dir):
        self.set_flipped(player_state, dir)
        safe = 99
        safed = 64
        self.full_overlap(player_state["PLAYER_X"] - self.PSZ[4], player_state["PLAYER_Y"] + self.PSZ[1], 0, self.PSZ[4] - self.PSZ[2])
        if self.toverlap > 0 and self.toverlap < safed:
            safe = 0
            safed = self.toverlap
        self.full_overlap(player_state["PLAYER_X"] - self.PSZ[4], player_state["PLAYER_Y"] - self.PSZ[3], 2, self.PSZ[4] - self.PSZ[2])
        if self.toverlap > 0 and self.toverlap < safed:
            safe = 2
            safed = self.toverlap
        self.full_overlap(player_state["PLAYER_X"] - self.PSZ[4], player_state["PLAYER_Y"] - self.PSZ[3], -1, self.PSZ[1] - self.PSZ[3])
        if self.toverlap > 0 and self.toverlap < safed:
            safe = -1
            safed = self.toverlap
        self.full_overlap(player_state["PLAYER_X"] + self.PSZ[2], player_state["PLAYER_Y"] - self.PSZ[3], 1, self.PSZ[1] - self.PSZ[3])
        if self.toverlap > 0 and self.toverlap < safed:
            safe = 1
            safed = self.toverlap
        if safe != 99:
            if safe > 0:
                if safe > 1:
                    player_state["PLAYER_Y"] += safed
                else:
                    player_state["PLAYER_X"] -= safed
            else:
                if safe > -1:
                    player_state["PLAYER_Y"] -= safed
                else:
                    player_state["PLAYER_X"] += safed
            self.resolve_collisions(False, player_state)
        
    def make_upright(self, player_state):
        if player_state["flipped"] == 0:
            return
        player_state["player_state"] = "spin"
        self.set_flipped_safe(player_state, 0)
        self.overlap = 0
            
    def fix_mask(self):
        try:
            self.mask_char = int(self.mask_char)
        except ValueError:
            self.mask_char = 0
            
    def check_square(self, x, y, psz):
        self.mask_char = self.get_block_at(x - psz[4], y - psz[3])
        self.fix_mask()

        if self.mask_char < 5:
            self.mask_char = self.get_block_at(x + psz[2], y - psz[3])
            self.fix_mask()

            if self.mask_char < 5:
                self.overlap = 0
                self.is_solid_at(x - psz[4], y + psz[1], 0)

                if self.overlap == 0:
                    self.is_solid_at(x + psz[2], y + psz[1], 0)

                    if self.overlap == 0:
                        self.mask_char = self.get_block_at(x - psz[4], y)
                        self.fix_mask()

                        if self.mask_char < 5:
                            self.mask_char = self.get_block_at(x + psz[2], y)
                            self.fix_mask()

                            if self.mask_char < 5:
                                self.mask_char = ""
                                return
        self.mask_char = 9
    
    def resolve(self, x, y, deep, player_state):
        psz = player_state["PSZ"]
        
        for i2 in range(1, deep + 1):
            i3 = -1
            for _ in range(8):
                i3 += 2
                player_state["PLAYER_X"] = x + (self.RESOLVE[i3] * i2)
                player_state["PLAYER_Y"] = y + (self.RESOLVE[i3 + 1] * i2)

                self.check_square(player_state["PLAYER_X"], player_state["PLAYER_Y"], psz)
                self.fix_mask()
                if self.mask_char < 5:
                    return

        player_state["PLAYER_X"] = x
        player_state["PLAYER_Y"] = y
        player_state["PLAYER_DEATH"] = "spike"
        
    def resolve_collisions(self, deep, player_state):
        self.check_square(player_state["PLAYER_X"], player_state["PLAYER_Y"], player_state["PSZ"])
        self.fix_mask()
        if self.mask_char < 5:
            return
        self.resolve(player_state["PLAYER_X"], player_state["PLAYER_Y"], 10 if deep else 4, player_state)
    
    def move_player_x(self, player_state):
        sx = player_state["PLAYER_SX"]
        psz = player_state["PSZ"]
        rem_x = player_state["PLAYER_X"]
        dir = 1 if sx > 0 else -1

        if sx > 0:
            player_state["PLAYER_X"] += sx + psz[2]
        else:
            player_state["PLAYER_X"] += sx - psz[4]

        self.overlap = 0
        self.is_solid_at(player_state["PLAYER_X"], player_state["PLAYER_Y"] + psz[1], dir)
        self.is_solid_at(player_state["PLAYER_X"], player_state["PLAYER_Y"], dir)
        self.is_solid_at(player_state["PLAYER_X"], player_state["PLAYER_Y"] - psz[3], dir)

        if self.overlap > 0:
            if self.overlap > (abs(sx) + 4):
                temp = player_state["PLAYER_X"]
                player_state["PLAYER_X"] = rem_x + sx
                self.resolve_collisions(False, player_state)
                if player_state["PLAYER_DEATH"] != 0:
                    player_state["PLAYER_X"] = temp
                    player_state["PLAYER_DEATH"] = "squish?"
                else:
                    return

            if sx > 0:
                player_state["PLAYER_X"] -= 0.01 + self.overlap
                self.touching_wall_dx(player_state, 1)
            else:
                player_state["PLAYER_X"] += 0.01 + self.overlap
                self.touching_wall_dx(player_state, -1)

            self.overlap = 0
            self.is_solid_at(player_state["PLAYER_X"], player_state["PLAYER_Y"] + psz[1], dir)
            self.is_solid_at(player_state["PLAYER_X"], player_state["PLAYER_Y"], dir)
            self.is_solid_at(player_state["PLAYER_X"], player_state["PLAYER_Y"] - psz[3], dir)

            if self.overlap > 0:
                player_state["PLAYER_DEATH"] = "1"
            player_state["PLAYER_SX"] *= 0.5

        player_state["PLAYER_X"] += -psz[2] if sx > 0 else psz[4]

        if player_state["PLAYER_X"] < 14 - 60:
            player_state["PLAYER_X"] = 14 - 60
            player_state["PLAYER_SX"] = 0
            
    def touching_wall_dy(self, player_state, up, dy):
        player_state["PLAYER_SY"] = 0
        if dy == 1 and up:
            player_state["PLAYER_SY"] = 4
            player_state["is_falling"] = 0
            player_state["player_wall"] = "0"
            self.set_flipped(player_state, 0)

    def move_player_y(self, player_state, up):
        dy = player_state["PLAYER_SY"]
        psz = player_state["PSZ"]

        dir = 0 if dy > 0 else 2
        
        if dy > 0:
            player_state["PLAYER_Y"] += dy + psz[1]
        else:
            player_state["PLAYER_Y"] += dy - psz[3]

        self.overlap = 0
        self.is_solid_at(player_state["PLAYER_X"] + psz[2], player_state["PLAYER_Y"], dir)
        self.is_solid_at(player_state["PLAYER_X"] - psz[4], player_state["PLAYER_Y"], dir)

        if self.overlap > 0:
            if dy > 0:
                player_state["PLAYER_Y"] -= 0.01 + self.overlap
                self.touching_wall_dy(player_state, up, 1)
                if "spin" in player_state["player_state"]:
                    player_state["player_state"] = ""
            else:
                player_state["PLAYER_Y"] += 0.01 + self.overlap
                self.touching_wall_dy(player_state, up, -1)
                player_state["is_falling"] = 0
                player_state["is_jumping"] = 0
                if player_state["player_wall"] != "2":
                    player_state["player_wall"] = ""
                if player_state["player_state"] == "wall spin":
                    player_state["player_state"] = ""

        player_state["PLAYER_Y"] -= psz[1] if dy > 0 else -psz[3]
            
    def set_flipped(self, player_state, flipped):        
        temp = (flipped % 4) + 1

        if player_state["player_wall"] == "" and player_state["player_state"] == "crouch":
            player_state["PSZ"][temp] = 7
        else:
            player_state["PSZ"][temp] = 17
        
        temp = (temp % 4) + 1
        player_state["PSZ"][temp] = 13
        temp = (temp % 4) + 1
            
        if player_state["player_wall"] != "" and player_state["player_state"] == "crouch":
            player_state["PSZ"][temp] = 7
        else:
            player_state["PSZ"][temp] = 17

        temp = (temp % 4) + 1
        player_state["PSZ"][temp] = 13
        player_state["flipped"] = flipped
            
    def can_get_up(self, player_state):
        self.overlap = 0
        psz = player_state["PSZ"]

        if player_state["flipped"] == 0:
            if player_state["player_wall"] == "0":
                self.is_solid_at(player_state["PLAYER_X"] - psz[4], (player_state["PLAYER_Y"] - psz[3]) - 8, 0)
                self.is_solid_at(player_state["PLAYER_X"] + psz[2], (player_state["PLAYER_Y"] - psz[3]) - 8, 0)
            else:
                self.is_solid_at(player_state["PLAYER_X"] - psz[4], player_state["PLAYER_Y"] + psz[1] + 8, 0)
                self.is_solid_at(player_state["PLAYER_X"] + psz[2], player_state["PLAYER_Y"] + psz[1] + 8, 0)

        elif player_state["flipped"] == 1:
            self.is_solid_at(player_state["PLAYER_X"] - psz[4] - 8, player_state["PLAYER_Y"] + psz[1], 1)
            self.is_solid_at(player_state["PLAYER_X"] - psz[4] - 8, player_state["PLAYER_Y"] - psz[3], 1)

        elif player_state["flipped"] == 2:
            self.is_solid_at(player_state["PLAYER_X"] - psz[4], (player_state["PLAYER_Y"] - psz[3]) - 8, 2)
            self.is_solid_at(player_state["PLAYER_X"] + psz[2], (player_state["PLAYER_Y"] - psz[3]) - 8, 2)
        else:
            self.is_solid_at(player_state["PLAYER_X"] + psz[2] + 8, player_state["PLAYER_Y"] + psz[1], -1)
            self.is_solid_at(player_state["PLAYER_X"] + psz[2] + 8, player_state["PLAYER_Y"] - psz[3], -1)
            
    def fix_dir(self):
        self.direction = self.direction % 360 - 360 if self.direction % 360 > 180 else self.direction % 360

    def position_now(self, player_state):
        if player_state["player_state"] == "wall spin":
            self.direction += 22.5 * player_state["flipped"]
            self.fix_dir()
            return
        if player_state["player_state"] == "spin":
            temp = ((((player_state["flipped"] + 1) * 90) - self.direction) + 180) % 360 - 180
            if abs(temp) < 22.5:
                self.direction = player_state["flipped"] * 90
                player_state["player_state"] = ""
            else:
                if temp < 0 and not(temp == -180 and self.direction == 0):
                    self.direction -= 30
                else:
                    self.direction += 30
                self.fix_dir()
                return
        self.direction = (player_state["flipped"] + 1) * 90
        self.fix_dir()

    def confirm_still_touching_wall(self, player_state):
        psz = player_state["PSZ"]

        self.overlap = 0
        if player_state["player_wall"] == "0":
            self.is_solid_at(player_state["PLAYER_X"], player_state["PLAYER_Y"] + psz[1] + 1, 0)

        if player_state["player_wall"] == "1":
            self.is_solid_at(player_state["PLAYER_X"] + psz[2] + 1, player_state["PLAYER_Y"], 0)
            self.is_solid_at(player_state["PLAYER_X"] + psz[2] + 1, player_state["PLAYER_Y"] - psz[3], 0)
  
        if player_state["player_wall"] == "-1":
            self.is_solid_at(player_state["PLAYER_X"] - psz[4] - 1, player_state["PLAYER_Y"], 0)

        if self.overlap == 0:
            if player_state["player_state"] == "crouch":
                if player_state["player_wall"] == "1":
                    player_state["PLAYER_X"] += 10
                elif player_state["player_wall"] == "-1":
                    player_state["PLAYER_X"] -= 10
                elif player_state["player_wall"] == "0":
                    player_state["PLAYER_Y"] += 10

            player_state["player_wall"] = ""
            self.set_flipped(player_state, player_state["flipped"])
            
    def handle_player_left_right(self, player_state, input_keys):
        max_speed = 1.2 if player_state["player_state"] == "crouch" else 2.5
        left, right = "A" in input_keys, "D" in input_keys

        if not (player_state["player_state"] == "wall spin" and player_state["is_falling"] < 25):
            if player_state["player_state"] == "wall spin" and player_state["is_falling"] < 35:
                max_speed *= (player_state["is_falling"] - 25) / 10

            if player_state["player_wall"] != "":
                if player_state["player_wall"] != "0":
                    if left and not "A" in self.last_tick_keys:
                        player_state["PLAYER_SX"] -= max_speed
                    if right and not "D" in self.last_tick_keys:
                        player_state["PLAYER_SX"] += max_speed
            else:
                if left:
                    player_state["PLAYER_SX"] -= max_speed
                if right:
                    player_state["PLAYER_SX"] += max_speed
                
            if player_state["player_state"] == "wall spin" and player_state["is_falling"] < 30:
                player_state["PLAYER_SX"] -= player_state["PLAYER_SX"] * 0.2 * (player_state["is_falling"] - 20)/ 10
            else:
                if abs(player_state["PLAYER_SX"]) < 1:
                    player_state["PLAYER_SX"] = 0
                else:
                    player_state["PLAYER_SX"] *= 0.8 if (left or right or abs(player_state["PLAYER_SX"]) > 2) else 0

        self.move_player_x(player_state )
        self.last_tick_keys = input_keys
    
    def start_wall_jump(self, player_state):
        player_state["is_jumping"] = 101
        player_state["player_state"] = "wall spin"
        try:
            player_wall = int(player_state["player_wall"])
        except ValueError:
            player_wall = 0

        self.set_flipped(player_state, 0 - player_wall)

        player_state["PLAYER_SY"] = 20
        player_state["PLAYER_SX"] = -10 * player_wall
        player_state["player_wall"] = ""
        player_state["is_falling"] = 10
        player_state["KEY_UP"] = 2

    def process_jump(self, player_state):
        if player_state["KEY_UP"] == 1:
            if "1" in player_state["player_wall"]:
                self.start_wall_jump(player_state)
            else:
                if player_state["is_jumping"] != 100:
                    if player_state["is_falling"] < 3 or (player_state["flipped"] == 1 and player_state["is_falling"] < 5):
                        self.overlap = 0
                        self.is_solid_at(player_state["PLAYER_X"] - player_state["PSZ"][4], player_state["PLAYER_Y"] + 15, -99)
                        self.is_solid_at(player_state["PLAYER_X"] + player_state["PSZ"][2], player_state["PLAYER_Y"] + 15, -99)
                        if (self.overlap == 0) and (player_state["PLAYER_SY"] < 16):
                            player_state["KEY_UP"] = 2
                            player_state["is_jumping"] += 1
                            player_state["PLAYER_SY"] = 16

        if (player_state["is_jumping"] > 0) and (player_state["is_jumping"] < 5):
            if player_state["PLAYER_SY"] < 16:
                player_state["PLAYER_SY"] = 16
            player_state["is_jumping"] += 1
            player_state["KEY_UP"] = 2
            
    def handle_player_up_down(self, player_state, input_keys):
        up = "W" in input_keys
        down = "S" in input_keys

        player_state["PLAYER_SY"] -= 1.7
        if player_state["PLAYER_SY"] < -30:
            player_state["PLAYER_SY"] = -30

        if "1" in player_state["player_wall"]:
            if player_state["PLAYER_SY"] < 0:
                player_state["PLAYER_SY"] -= player_state["PLAYER_SY"] * 0.3

        if up:
            if player_state["KEY_UP"] < 1:
                player_state["KEY_UP"] = 1
        else:
            player_state["KEY_UP"] = 0

        if player_state["KEY_UP"] > 0:
            self.process_jump(player_state)
        else:
            if (player_state["is_jumping"] > 0) and (player_state["is_jumping"] < 100):
                player_state["is_jumping"] = 100
            if player_state["PLAYER_SY"] > 0 and player_state["is_falling"] > 1 and player_state["player_state"] == "":
                player_state["PLAYER_SY"] -= 1

        if down:
            if not "spin" in player_state["player_state"]:
                player_state["player_state"] = "crouch"
                self.set_flipped(player_state, player_state["flipped"])
                self.resolve_collisions(False, player_state)
        elif player_state["player_state"] == "crouch":
            self.can_get_up(player_state)
            if self.overlap == 0:
                player_state["player_state"] = ""
                self.set_flipped(player_state, player_state["flipped"])
                self.resolve_collisions(False, player_state)

        player_state["is_falling"] += 1
        self.move_player_y(player_state, up)
        
    def tick(self, player_state, input_keys):
        self.resolve_collisions(False, player_state)
        self.handle_player_up_down(player_state, input_keys)
        self.handle_player_left_right(player_state, input_keys)
        if player_state["player_wall"] != "":
            if player_state["player_wall"] == "0":
                player_state["is_falling"] = 10
            else:
                player_state["is_falling"] = 0
            self.confirm_still_touching_wall(player_state)

        if not "spin" in player_state["player_state"]:
            if player_state["flipped"] != 0 and player_state["player_wall"] == "":
                self.make_upright(player_state)

        self.position_now(player_state)
            
        return player_state

def create_default_player_state(x=128, y=280):
    return {
        "PLAYER_X": x,
        "PLAYER_Y": y,
        "PLAYER_SX": 0,
        "PLAYER_SY": 0,
        "PLAYER_DEATH": 0,
        "PSZ": [0 , 17, 13, 17, 13],
        "is_jumping": 0,
        "is_falling": 999,
        "on_ceiling": False,
        "KEY_UP": 0,
        "flipped": 0,
        "player_state": "",
        "player_wall": ""
    }

def get_data_from_code(code):
    """Parse a level code into map data and properties."""
    data = code[7:].split("Z")
    LSX = data[0]
    MAP_data = data[1:data.index("")]
    data = data[data.index("") + 1:]
    MAP_R_data = data[:data.index("")]
    MAP = []
    MAP_R = []
    
    # Parse MAP data (tile types)
    for i in range(0, len(MAP_data), 2):
        value = MAP_data[i]
        count = int(MAP_data[i + 1])
        if count > 99999:
            raise ValueError("This code will crash your computer.")
        MAP.extend([value] * count)
    
    # Parse MAP_R data (rotations)
    for i in range(0, len(MAP_R_data), 2):
        value = MAP_R_data[i]
        count = int(MAP_R_data[i + 1])
        if count > 99999:
            raise ValueError("This code will crash your computer.")
        MAP_R.extend([value] * count)
    
    # Return parsed data
    return {
        'map': [int(float(x)) for x in MAP],
        'rotations': [int(float(r)) for r in MAP_R],
        'LSX': int(LSX),
        'hue': int(data[-2]),
        'hue2': int(data[-1])
    }

def key_code(keys):
    code = str(
        int("D" in keys)
        + int("A" in keys) * 2
        + int("S" in keys) * 4
        + int("W" in keys) * 8
    )
    return code

def generate_replay_code(inputs, level=11, username="bruteforcer"):
    try:
        output = ""
        for i in range(len(inputs)):
            keys = inputs[i]  # Each element is now a string of keys for that frame
            if i == 0 or inputs[i] != inputs[i - 1]:  # Compare current frame to previous
                output += f"Ǉ{i+1}Ǉ{key_code(keys)}"
        output = f"{username}ǇǇ{level + 1}Ǉ1{output}Ǉ{len(inputs)+1}Ǉ0"
        return f"{len(output) + 12345678}{output}"
    except UnboundLocalError:
        return "Nothing was found"

def decode_replay_code(replay_code):
    try:
        s = str(replay_code)
        data = s[-(int(s[:-len(s[8:])]) - 12345678):].split('Ǉ')
        inputs = [""] * (int(data[-2]) - 1)
        changes = [(int(data[i]) - 1, "".join(k for k, b in [("D",1),("A",2),("S",4),("W",8)] if int(data[i+1]) & b)) 
                  for i in range(4, len(data)-2, 2)]
        for i, (start, keys) in enumerate(changes):
            inputs[start:changes[i+1][0] if i+1 < len(changes) else len(inputs)] = [keys] * (
                (changes[i+1][0] if i+1 < len(changes) else len(inputs)) - start)
        return inputs
    except:
        return "Error decoding replay"

def simulate_player(initial_state, key_frames, map, map_rotations, level_size_x):
    physics = appel_physics(map, map_rotations, level_size_x)
    player_state = initial_state.copy()
    
    for frame, keys in enumerate(key_frames):
        player_state = physics.tick(player_state, keys)
        print(player_state)
        if player_state['PLAYER_DEATH'] != 0:
            break
    
    return player_state