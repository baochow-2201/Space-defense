# src/engine/collision.py
import pygame

def bullets_hit_enemies(player_bullets_group, enemies_group, score_holder):
    hits = pygame.sprite.groupcollide(enemies_group, player_bullets_group, False, True)
    for enemy, bullets in hits.items():
        for b in bullets:
            enemy.hp -= getattr(b, "damage", 1)
        if enemy.hp <= 0:
            enemy.kill()
            score_holder["score"] += getattr(enemy, "score_value", 10)

def enemy_bullets_hit_player(enemy_bullets_group, player_sprite):
    hits = pygame.sprite.spritecollide(player_sprite, enemy_bullets_group, True)
    total_damage = 0
    for b in hits:
        total_damage += getattr(b, "damage", 1)
    if total_damage > 0:
        player_sprite.hp -= total_damage
    return total_damage
