import unittest
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler
handler = logging.FileHandler('GraphLogger')
handler.setLevel(logging.INFO)

# Add the handler to the logger
logger.addHandler(handler)


class Graph:

    def __init__(self):
        self.activity_list = []
        self.critical_path = []
        self.critical_path_temp = []
        self.longest_path = 0
        self.path_temp = 0

    def find_critical_path(self, activity_first):

        logger.debug('Function find_critical_path - the running activity is: , ', activity_first.name)

        if not activity_first.next:

            # Save last element in critical temp and add duration to long path
            self.critical_path_temp.append(activity_first)
            self.path_temp += activity_first.duration

            if self.longest_path < self.path_temp:
                self.longest_path = self.path_temp
                self.critical_path = self.critical_path_temp[:]

            # At last element the early finish ins always the length of the critical path
            activity_first.early_start = self.longest_path - activity_first.duration
            activity_first.early_finish = self.longest_path

            self.path_temp -= activity_first.duration
            self.critical_path_temp = self.critical_path_temp[:-1]
            return

        for a in activity_first.next:

            # Determine for activity early start and early finish
            self.check_early_start_and_early_finish(a, activity_first)

            # Save activity to temp list
            self.critical_path_temp.append(activity_first)

            # Add value to longest path
            self.path_temp += activity_first.duration

            self.find_critical_path(a)

            # Sub from path_temp variable an pop the last element
            self.path_temp -= activity_first.duration

            self.critical_path_temp = self.critical_path_temp[:-1]

    @staticmethod
    def check_early_start_and_early_finish(next_activity, current_activity):

        logger.debug('Function check_early_start_and_early_finish - the running activity is: , ', current_activity.name)

        # Determine for activity early start and early finish
        if not current_activity.previous:
            current_activity.early_start = 0
            current_activity.early_finish = current_activity.early_start + current_activity.duration

        # Check one elements beck early finish and determine early start

        # For first try
        if next_activity.early_start is None:
            next_activity.early_start = current_activity.early_finish

        # For the rest iterations
        elif next_activity.early_start is not None and next_activity.early_start < current_activity.early_finish:
            next_activity.early_start = current_activity.early_finish
        next_activity.early_finish = next_activity.early_start + next_activity.duration

    def find_slacks_time(self, recursion_activity, first_activity):

        logger.debug('Function find_slacks_time - the running activity is: ', recursion_activity.name)

        for a in recursion_activity.previous:
            # In the first activity
            if a == first_activity:
                return

            # In first iteration, for last activity - the late finish is always the critical path time
            if not recursion_activity.next:
                recursion_activity.late_finish = self.longest_path
                recursion_activity.late_start = self.longest_path - recursion_activity.duration
                recursion_activity.slacks_time = recursion_activity.late_start - recursion_activity.early_start

            # Check elements forward and determine late_finish

            # For first iteration
            if a.late_finish is None:
                a.late_finish = recursion_activity.late_start

            # For the rest iterations
            elif a.late_finish is not None and a.late_finish > recursion_activity.late_start:
                a.late_finish = recursion_activity.late_start

            a.late_start = a.late_finish - a.duration
            a.slacks_time = a.late_start - a.early_start

            self.find_slacks_time(a, first_activity)

    def add_activity(self, activity_to_add, first_activity, last_activity):
        logger.info('Function add_activity has start')
        # Add activity to list
        self.activity_list.append(activity_to_add)

        # Reset activities before calculate new slack time
        self.reset_details()

        # Create connections between activities
        for a in self.activity_list:
            if a in activity_to_add.next:
                a.previous.append(activity_to_add)
            if a in activity_to_add.previous:
                a.next.append(activity_to_add)

        # Determine new critical path and new slack time
        self.find_critical_path(first_activity)
        self.find_slacks_time(last_activity, first_activity)

        logger.info('Function add_activity has finish')

    def remove_activity(self, activity, activity_first, activity_end):

        logger.info('Function remove_activity has start')

        # Find activity in list
        for a in self.activity_list:
            if a == activity:
                # Get to previous activities pointer
                for x in a.previous:
                    # Change previous activity next attribute
                    for z in x.next:
                        if z == a:
                            x.next.remove(z)
                for x in a.next:
                    # Change next activity previous attribute
                    for z in x.previous:
                        if z == a:
                            x.previous.remove(z)

        self.activity_list.remove(activity)
        # Determine new critical path and new slack time
        self.reset_details()
        self.find_critical_path(activity_first)
        self.find_slacks_time(activity_end, activity_first)

        logger.info('Function remove_activity has finish')
        return

    def validate_project_step1(self):
        logger.info('Function validate_project_step1 has start')
        # Reset critical_path_temp
        self.critical_path_temp.clear()
        for a in self.activity_list:
            self.path_temp = 0
            self.validate_project_step2(a, a)

        # Print circles activities details
        print("\nCircles Activities:\n")
        print("Activity    Duration")
        for w in self.critical_path_temp:
            print("  ", w.name, "         ", w.duration)

        logger.info('Function validate_project_step1 has finish')

    def validate_project_step2(self, activity, activity_to_check):
        if not activity.next:
            return

        for a in activity.next:
            # Add value to longest path
            self.path_temp += activity.duration

            if activity_to_check in activity.next:
                self.critical_path_temp.append(activity_to_check)
                return

            # In case there is a circle in graph
            if self.path_temp > self.longest_path * 2:
                return

            self.validate_project_step2(a, activity_to_check)

            # Sub from path_temp variable an pop the last element
            self.path_temp -= activity.duration

    def find_isolate_activity(self):

        logger.info('Function find_isolate_activity has start')

        self.critical_path_temp.clear()

        for a in self.activity_list:
            if not a.next or not a.previous:
                self.critical_path_temp.append(a)

        logger.info('Function find_isolate_activity has finish')

    def __str__(self):
        logger.debug('Function __str__(Graph) has start')
        result = "Graph \nActivities in project: \n"
        for a in self.activity_list:
            result += str(a)

        result += "\n\nCritical path: \n| "
        for a in self.critical_path:
            result += a.name + " | "

        result += "\n\nProject duration: " + str(self.longest_path) + "\n\n"

        logger.info('Function __str__(Graph) has finish')
        return result

    def reset_details(self):
        logger.info('Function reset_details has start')
        # Reset activities before calculate new slack time
        for a in self.activity_list:
            a.late_start = None
            a.early_start = None
            a.late_finish = None
            a.late_start = None
        self.longest_path = 0
        logger.info('Function reset_details has finish')


class Activity:

    def __init__(self, name, _next, previous, duration, early_finish, early_start, late_start,
                 late_finish, slacks_time):

        # Name of current activity
        self.name = name

        # Next is a list of activities
        self.next = _next

        # Previous is a list of activities
        self.previous = previous

        self.duration = duration
        self.early_finish = early_finish
        self.early_start = early_start
        self.late_start = late_start
        self.late_finish = late_finish
        self.slacks_time = slacks_time

    def __str__(self):
        logger.info('Function __str__(Activity) has start')
        result = "\n\nName: " + self.name + "\n" + "Duration: " + str(self.duration) + "\n" + \
                 "Early start: " + str(self.early_start) + "\n" + "Early finish: " + str(self.early_finish) + "\n" + \
                 "Late start: " + str(self.late_start) + "\n" + "late finish: " + str(self.late_finish) + "\n" + \
                 "Slacks time: " + str(self.slacks_time) + "\n" + \
                 "Next: "

        for a in self.next:
            result += a.name + " "

        result += "\nPrevious: "
        for a in self.previous:
            result += a.name + " "

        logger.info('Function __str__(Activity) has finish')
        return result


class TestGraph(unittest.TestCase):
    graph = Graph()
    # Start activity
    start = Activity("St", [], [], 0, 0, 0, 0, 0, 0)
    # Middle activities
    a = Activity("A*", [], [], 4, None, None, None, None, None)
    b = Activity("B*", [], [], 2, None, None, None, None, None)
    c = Activity("C*", [], [], 2, None, None, None, None, None)
    d = Activity("D*", [], [], 5, None, None, None, None, None)
    e = Activity("E*", [], [], 6, None, None, None, None, None)
    f = Activity("F*", [], [], 4, None, None, None, None, None)
    g = Activity("G*", [], [], 6, None, None, None, None, None)
    h = Activity("H*", [], [], 5, None, None, None, None, None)
    i = Activity("I*", [], [], 5, None, None, None, None, None)
    j = Activity("J*", [], [], 8, None, None, None, None, None)
    # Last activity
    end = Activity("En", [], [], 0, None, None, None, None, None)
    # Create activity for testing
    temp_activity = Activity(None, None, None, None, None, None, None, None, None)

    def add_activity_to_list(self):
        logger.info('Function add_activity_to_list has start')
        self.graph.activity_list.append(self.start)
        self.graph.activity_list.append(self.a)
        self.graph.activity_list.append(self.b)
        self.graph.activity_list.append(self.c)
        self.graph.activity_list.append(self.d)
        self.graph.activity_list.append(self.e)
        self.graph.activity_list.append(self.f)
        self.graph.activity_list.append(self.g)
        self.graph.activity_list.append(self.h)
        self.graph.activity_list.append(self.i)
        self.graph.activity_list.append(self.j)
        self.graph.activity_list.append(self.end)
        logger.info('Function add_activity_to_list has finish')

    def create_connection(self):
        logger.info('Function create_connection has start')
        # Next connections
        self.start.next = [self.a, self.e, self.i]
        self.a.next = [self.b]
        self.b.next = [self.f, self.g, self.c, self.j, self.h]
        self.c.next = [self.end]
        self.d.next = [self.end]
        self.e.next = [self.b]
        self.f.next = [self.g]
        self.g.next = [self.end]
        self.h.next = [self.d, self.g]
        self.i.next = [self.f]
        self.j.next = [self.end]

        # Previous connections
        self.start.previous = []
        self.a.previous = [self.start]
        self.b.previous = [self.e, self.a]
        self.c.previous = [self.b]
        self.d.previous = [self.h]
        self.e.previous = [self.start]
        self.f.previous = [self.b, self.i]
        self.g.previous = [self.f, self.b, self.h]
        self.h.previous = [self.b]
        self.i.previous = [self.start]
        self.j.previous = [self.b]
        self.end.previous = [self.j, self.d, self.g, self.c]

        logger.info('Function create_connection has finish')

    def test_1(self):
        print("\nQuestion 7 - 8: Critical Time and Slack Time")
        # Create and initial data in graph

        self.create_connection()
        self.add_activity_to_list()

        # Find and print critical path
        self.graph.find_critical_path(self.start)
        print("The critical path is: ")
        print("Activity", " ", "Duration")
        for x in self.graph.critical_path:
            print("  ", x.name, "        ", x.duration)

        # Find and print slack time for each activity
        self.graph.find_slacks_time(self.end, self.start)

        print("\nThe slack time for each activity is: \n")
        print("Activity", " ", "Slack time")
        for x in self.graph.activity_list:
            print("  ", x.name, "        ", x.slacks_time)
        print("\n------------------------------------------------------------------------------\n")

    def test_2(self):
        print("\nQuestion 2: Add activity")

        # Create activity to add
        print("\nGraph details before add temp_activity:")
        print(self.graph.__str__())

        # Create activity to add
        self.temp_activity.name = "Temp activity"
        self.temp_activity.duration = 3
        self.temp_activity.next = [self.h]
        self.temp_activity.previous = [self.e]
        self.temp_activity.late_start = None
        self.temp_activity.late_finish = None
        self.temp_activity.early_finish = None
        self.temp_activity.early_start = None
        self.temp_activity.slacks_time = None
        self.graph.add_activity(self.temp_activity, self.start, self.end)

        print("\n\nGraph details after add temp_activity:")
        print(self.graph.__str__())
        print("\n------------------------------------------------------------------------------\n")

    def test_3(self):
        print("\nQuestion 3: Remove activity")
        print("\nLets remove the temp_activity that added in test 2")

        self.graph.remove_activity(self.temp_activity, self.start, self.end)

        print("\nAfter remove temp_activity\n")
        print(self.graph.__str__())
        print("\n------------------------------------------------------------------------------\n")

    def test_4(self):
        print("\nQuestion 4: validate project")
        print("\nCreate a connection between activity b to activity start")
        print("\nIn this case - start activity is a circle")

        # Add to activity d in next attribute the activity b
        # In this case it create a circle of c , d, b
        self.d.next.append(self.b)
        self.graph.validate_project_step1()
        print("\n------------------------------------------------------------------------------\n")

    def test_5(self):
        print("\nQuestion 5: Find isolate activities")
        # For checking - add isolate activity n
        n = Activity("N_", [self.a], [], 3, None, None, None, None, None)
        self.graph.activity_list.append(n)

        self.graph.find_isolate_activity()
        print("\nIsolate Activities")
        for a in self.graph.critical_path_temp:
            print("  ", a.name, "      ", a.duration)
        print("\n------------------------------------------------------------------------------\n")

    def test_6(self):
        print("\nQuestion 9: The duration of the project is: ", self.graph.longest_path)
        print("\n------------------------------------------------------------------------------\n")


if __name__ == "__main__":
    unittest.main()














