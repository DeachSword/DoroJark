import json
from DoroJark.main import DoroJark
from DoroJark.models.chart import Chart

VIEWER_VERS = {
    "1": "v1.0.0",
    "3": "v1.0.3",
    "4": "v1.0.4",
    "5": "v1.0.5",
    "6": "v1.0.6",
}

if __name__ == "__main__":
    CHART_ID = "5030036"
    DIFF = "1"
    VIEW_VER = "6"

    DEVICE_TOKEN = input("Device Token for login game: ")
    GAME_SERVER_REGION = input("Region for game server: ")

    while len(CHART_ID) < 7:
        CHART_ID = f"0{CHART_ID}"
    if DIFF not in ["1", "2", "3", "4"]:
        raise RuntimeError("No Entity (e: 34)")
    else:
        CHART_ID = f"{CHART_ID}{DIFF}"

    if len(CHART_ID) != 8:
        raise RuntimeError("No Entity (e: 35)")
    if VIEW_VER not in VIEWER_VERS:
        raise RuntimeError("No Entity (e: 39)")

    try:
        D4DJClient = DoroJark(DEVICE_TOKEN, "", region=GAME_SERVER_REGION)
        with open(rf"./chart_{CHART_ID}.json") as f:
            chart_file = f.read()
            chart_data = json.loads(chart_file)
            chart = Chart(D4DJClient, chart_data)
            if chart.APP_VER != VIEWER_VERS[VIEW_VER]:
                raise RuntimeError("No Entity (e: 41)")
            chart.renderTo(r"./test_res.png")
    except NotImplementedError as ex:
        pass
    except Exception as ex:
        if str(ex) != "resp not 200":
            raise ex
    print("Done!")
