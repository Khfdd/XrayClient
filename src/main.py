import constants
import questionary
import typing
import json
import subscription
import enum
import datetime


class Flags(enum.Enum):
    ADD_SUB = "➕ Добавить подписку"
    UPDATE_SUB = "🔄 Обновить подписку"
    BACK_ACTION = "🔙 Назад"


def main():
    while True:
        with subscription.SubscriptionManager(constants.DATA_DIR, headers=constants.HEADERS) as sub_manager:
            sub: subscription.Subscription | Flags = questionary.select(
                "Выберите подписку:",
                choices=[
                    questionary.Choice(i.name, value=i)
                    for i in sorted(sub_manager.subs)
                ] + [
                    questionary.Choice(
                        title=Flags.ADD_SUB.value, value=Flags.ADD_SUB),
                    questionary.Choice(
                        title=Flags.BACK_ACTION.value, value=Flags.BACK_ACTION)
                ]
            ).ask()

            if sub == Flags.ADD_SUB:
                new_sub = input("Введите url подписки: ")
                sub_manager.add_sub(new_sub).show()
            elif sub == Flags.BACK_ACTION:
                print("Вы вышли из программы.")
                break
            elif isinstance(sub, subscription.Subscription):
                if sub.last_updated:
                    time_delta = datetime.datetime.now(
                        datetime.UTC).timestamp() - sub.last_updated
                    print(
                        f"⏱️ Updated: {time_delta // 86400} days {(time_delta // 3600) % 24} hours {(time_delta // 60) % 60} minutes ago.")
                else:
                    print(
                        f"⏱️ Updated: Unknown ago.")
                config: dict[str, typing.Any] | Flags = questionary.select(
                    "Выберите конфиг:",
                    choices=[
                        questionary.Choice(
                            title=Flags.UPDATE_SUB.value, value=Flags.UPDATE_SUB),

                        questionary.Choice(
                            title=Flags.BACK_ACTION.value, value=Flags.BACK_ACTION)
                    ]+[
                        questionary.Choice(
                            title=f'{config.get("remarks", "N/A")} [{sum(1 for i in config.get("outbounds", []) if i.get("protocol") not in ["freedom", "blackhole"])}]', value=config)
                        for config in sub.config
                    ],
                ).ask()

                if config == Flags.UPDATE_SUB:
                    sub.update()
                elif config == Flags.BACK_ACTION:
                    continue
                elif isinstance(config, dict):
                    config["inbounds"] = constants.INBOUNDS
                    with open(constants.XRAY_CONFIG_FILE, "w", encoding="utf8") as file:
                        json.dump(config, file, ensure_ascii=False, indent=4)
                    if sub.geoip:
                        with open(constants.XRAY_GEOIP_FILE, "wb") as file:
                            file.write(sub.geoip)
                    if sub.geosite:
                        with open(constants.XRAY_GEOSITE_FILE, "wb") as file:
                            file.write(sub.geosite)
                    break


if __name__ == "__main__":
    main()
