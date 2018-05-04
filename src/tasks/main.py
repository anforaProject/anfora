from tasks.config import huey  # import our "huey" object
from tasks.tasks import count_beans  # import our task


if __name__ == '__main__':
    beans = input('How many beans? ')
    count_beans(int(beans))
    print('Enqueued job to count %s beans' % beans)
