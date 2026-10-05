import pygame
import random
import sys

# Oyun Ayarları
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60

# Renkler (RGB)
SKY_BLUE = (135, 206, 235)
DIRT_COLOR = (139, 69, 19)
GRASS_COLOR = (34, 139, 34)
PLAYER_COLOR = (255, 105, 180) # Pembe/Kız karakter veya standart insan simgesi
TEXT_COLOR = (255, 255, 255)
INV_BG_COLOR = (50, 50, 50)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50) # Karakter boyutu
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.jump_power = -12
        self.is_grounded = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = self.speed
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.is_grounded:
            self.vy = self.jump_power
            self.is_grounded = False

    def update(self, world_blocks):
        # Yerçekimi Uygulama
        self.vy += 0.6
        if self.vy > 15:
            self.vy = 15

        # Yatay Hareket ve Çarpışma Testi
        self.rect.x += self.vx
        for block_rect in world_blocks.values():
            if self.rect.colliderect(block_rect):
                if self.vx > 0:
                    self.rect.right = block_rect.left
                elif self.vx < 0:
                    self.rect.left = block_rect.right

        # Dikey Hareket ve Çarpışma Testi
        self.rect.y += self.vy
        self.is_grounded = False
        for block_rect in world_blocks.values():
            if self.rect.colliderect(block_rect):
                if self.vy > 0:
                    self.rect.bottom = block_rect.top
                    self.vy = 0
                    self.is_grounded = True
                elif self.vy < 0:
                    self.rect.top = block_rect.bottom
                    self.vy = 0

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mini Terra Clone - Python")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Dünya Oluşturma (Grid Sistemi)
    # Key: (grid_x, grid_y), Value: pygame.Rect
    world_blocks = {}
    block_types = {} # Blok türlerini tutar: 'grass' veya 'dirt'
    
    cols = SCREEN_WIDTH // TILE_SIZE
    rows = SCREEN_HEIGHT // TILE_SIZE

    # Basit bir arazi jeneratörü (Toprak ve Çimen çizgisi)
    for cx in range(cols):
        # 8 ile 12. satırlar arasında rastgele bir zemin yüksekliği yapalım
        ground_level = random.randint(9, 11)
        for cy in range(ground_level, rows):
            rect = pygame.Rect(cx * TILE_SIZE, cy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            world_blocks[(cx, cy)] = rect
            if cy == ground_level:
                block_types[(cx, cy)] = 'grass'
            else:
                block_types[(cx, cy)] = 'dirt'

    # Oyuncu Başlangıç Pozisyonu (Ekranın ortasında, havada başlasın yere düşecek)
    player = Player(SCREEN_WIDTH // 2, 100)

    # Basit Envanter Sistemi
    # 'grass': adet, 'dirt': adet
    inventory = {'grass': 0, 'dirt': 0}
    selected_block_type = 'dirt' # Elimizde seçili olan blok

    # Oyun Döngüsü
    running = True
    while running:
        clock.tick(FPS)
        
        # Olay (Event) Yönetimi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Fare Tıklamaları (Sol tık: Kazma, Sağ tık: Koyma)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                grid_x = mouse_pos[0] // TILE_SIZE
                grid_y = mouse_pos[1] // TILE_SIZE
                
                # Sol Tık: Blok Kırma (Maden/Kazma)
                if event.button == 1: 
                    if (grid_x, grid_y) in world_blocks:
                        b_type = block_types[(grid_x, grid_y)]
                        inventory[b_type] += 1 # Envantere ekle
                        
                        del world_blocks[(grid_x, grid_y)]
                        del block_types[(grid_x, grid_y)]
                        
                # Sağ Tık: Blok Yerleştirme
                elif event.button == 3: 
                    if (grid_x, grid_y) not in world_blocks:
                        if inventory[selected_block_type] > 0:
                            # Karakterin tam üstüne blok koyulmasını engellemek için basit kontrol
                            new_rect = pygame.Rect(grid_x * TILE_SIZE, grid_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                            if not player.rect.colliderect(new_rect):
                                world_blocks[(grid_x, grid_y)] = new_rect
                                block_types[(grid_x, grid_y)] = selected_block_type
                                inventory[selected_block_type] -= 1

            # Klavye ile Envanter Seçimi Değiştirme (1 ve 2 tuşları)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_block_type = 'dirt'
                elif event.key == pygame.K_2:
                    selected_block_type = 'grass'

        # Güncellemeler
        player.handle_input()
        player.update(world_blocks)

        # Çizim Aşaması
        screen.fill(SKY_BLUE) # Gökyüzü

        # Blokları Çiz
        for coord, rect in world_blocks.items():
            color = GRASS_COLOR if block_types[coord] == 'grass' else DIRT_COLOR
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1) # Blok sınır çizgileri

        # Karakteri Çiz
        player.draw(screen)

        # Envanter Arayüzü (UI) Çizimi
        pygame.draw.rect(screen, INV_BG_COLOR, pygame.Rect(10, 10, 220, 80))
        
        # Yazıları Hazırla
        txt_info = "Sol Tik: Kaz | Sag Tik: Koy"
        txt_inv1 = f"[1] Toprak (Dirt): {inventory['dirt']}" + (" <-" if selected_block_type == 'dirt' else "")
        txt_inv2 = f"[2] Cimen (Grass): {inventory['grass']}" + (" <-" if selected_block_type == 'grass' else "")
        
        surf_info = font.render(txt_info, True, TEXT_COLOR)
        surf_inv1 = font.render(txt_inv1, True, TEXT_COLOR)
        surf_inv2 = font.render(txt_inv2, True, TEXT_COLOR)
        
        screen.blit(surf_info, (20, 15))
        screen.blit(surf_inv1, (20, 40))
        screen.blit(surf_inv2, (20, 60))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()