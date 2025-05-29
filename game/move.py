def simple_attack(attacker, defender):
    messages = []
    cost = 10

    if attacker.energy < cost:
        attacker.consume_energy(attacker.energy)  # lo que tenga
        messages.append(f"{attacker.name} intentó usar {attacker.simple_attack_name}, pero no tuvo suficiente energía.")
        return messages

    attacker.consume_energy(cost)
    messages.append(f"{attacker.name} usó {attacker.simple_attack_name}.")

    damage = defender.receive_damage(10)
    if damage == 0:
        messages.append("El movimiento fue bloqueado.")
    else:
        messages.append("El movimiento funcionó.")
        messages.append(f"Causó {damage} de daño y perdió {cost} de energía.")

    return messages


def defense(character):
    messages = []
    cost = 5

    if character.energy < cost:
        character.consume_energy(character.energy)
        messages.append(f"{character.name} intentó usar {character.defense_name}, pero no tuvo suficiente energía.")
        return messages

    character.consume_energy(cost)
    character.defend()

    messages.append(f"{character.name} se preparó con {character.defense_name}.")
    messages.append("El próximo ataque será parcialmente bloqueado.")
    messages.append(f"Perdió {cost} de energía.")

    return messages


def strong_attack(attacker, defender):
    messages = []
    cost = 25

    if attacker.energy < cost:
        attacker.consume_energy(attacker.energy)
        messages.append(f"{attacker.name} intentó usar {attacker.strong_attack_name}, pero no tuvo suficiente energía.")
        return messages

    attacker.consume_energy(cost)
    messages.append(f"{attacker.name} lanzó {attacker.strong_attack_name}.")

    damage = defender.receive_damage(25)
    if damage == 0:
        messages.append("El movimiento fue bloqueado.")
    else:
        messages.append("El movimiento fue devastador.")
        messages.append(f"Causó {damage} de daño y perdió {cost} de energía.")

    return messages


def special_power(attacker):
    messages = []
    cost = 40
    heal = 10

    if attacker.energy < cost:
        attacker.consume_energy(attacker.energy)
        messages.append(f"{attacker.name} intentó usar {attacker.special_power_name}, pero no tuvo suficiente energía.")
        return messages

    attacker.consume_energy(cost)
    attacker.restore_health(heal)

    messages.append(f"{attacker.name} activó {attacker.special_power_name}.")
    messages.append(f"Recuperó {heal} de vida.")
    messages.append(f"Perdió {cost} de energía.")

    return messages