import datetime
import json
import shutil
import sys
import traceback
import os

if __name__ == "__main__":
    run_everything = False
    if len(sys.argv) >= 2:
        try:
            if sys.argv[1] == "all":
                run_everything = True
                day_number = 1
            else:
                day_number = int(sys.argv[1])
        except Exception:
            print("{} - Runs a given AoC day (or the current day if no arguments are given)".format(sys.argv[0]))
            print("Usage: {} [day]".format(sys.argv[0]))
            sys.exit(1)
    else:
        day_number = datetime.date.today().day

    if day_number <= 0 or day_number > 25:
        print("Day given is out of range 1-25.")
        sys.exit(2)

    if os.path.isfile("settings.json"):
        with open("settings.json", 'r') as s:
            settings = json.loads("".join(s.readlines()))
    else:
        shutil.copy("settings.json.default", "settings.json")
        print("Please fill in settings.json first!")
        sys.exit(3)

    session_token = settings['session_token']
    year = settings['year']

    days_to_run = [day_number]
    if run_everything:
        days_to_run = [x+1 for x in range(25)]

    # Dynamically try to load the requested day
    from days import *
    from aocdays import AOCDays
    days: AOCDays = AOCDays.get_instance()

    for d in days_to_run:
        day = days.get_day(d)

        if day:
            for someones_day in day:
                print("Attempting to run AoC day {} from {}...".format(d, someones_day.creator))
                # noinspection PyBroadException
                try:
                    instance = someones_day(year, d, session_token)
                    instance.run()
                except ConnectionError as e:
                    print(e, file=sys.stderr)
                except Exception as e:
                    traceback.print_exc()
        else:
            if d == datetime.date.today().day:
                # This is today, create it!
                template_filename = os.path.join(os.path.dirname(__file__), "days/_template.py")
                newday_filename = os.path.join(os.path.dirname(__file__), "days/day{}.py".format(d))
                shutil.copy(template_filename, newday_filename)
                with open(newday_filename, 'r') as f:
                    lines = f.readlines()
                lines = [x.replace("@day(0)", "@day({})".format(d)) for x in lines]
                with open(newday_filename, 'w') as f:
                    f.writelines(lines)

                print("Files for day {} created! Happy coding and good luck!".format(d))
            else:
                print("Attempting to run AoC day {}...".format(d))
                print("I have nothing to run for day {}".format(d))

