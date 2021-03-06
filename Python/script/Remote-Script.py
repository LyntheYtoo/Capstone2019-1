import iot.ThingsSerial as ts
import sys
import platform
import glob
import serial
from datetime import datetime

# 통신용 전역변수
sensor_data_list = ""
sensing_pointer = 0

# 역치값
Threshole = 25.0
event_trigger = False
main_loop = True


class ThingsMangement(ts.ThingsSerial):
    # 사전
    things_pointer = 0

    things_list = []
    sensor_data_list = []

    sensing_data_list = []

    global sensing_pointer

    sensing_pointer = 0

    # 생성자 장치들 파악 후 등록

    def __init__(self):

        COM_port_list = self.serial_ports()

        for com in COM_port_list:
            print("Serial port > ", com, " processing")
            things = ts.ThingsSerial(self.things_pointer,com, 9600)
            self.add_things(things)
            print("things pointer > ", self.things_pointer)

        print("things register done")

    # 장치 등록 ThingsMain 객체를 추가하기
    def add_things(self, source):
        self.things_list.append(source)
        self.things_pointer = self.things_pointer + 1

    def sensor_scheduling(self,things):
        data = things.serial_readline()
        data = data.strip()
        data = float(data)

        if data:
            date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            print(date)
            print("things ID: ", things.id)
            print("Things Role: ", things.role)
            print("things COM: ", things.port_number)
            print("things baudrate: ", things.baudrate)
            print("things Data: ", data)

            self.sensing_data_list.append(data)

            # ######################## 여기서 최종적으로 버퍼에다 데이터 쓰기
            global sensor_data_list

            #sensor_data_list = sensor_data_list + data + ","
            sensor_data_list = {"id": things.id, "date": date, "data": data}

            global sensing_pointer

            sensing_pointer = sensing_pointer + 1

    # 상황처리테이블에 따라 팬속도 조절 동적/정적 가능
    def fan_scheduling(self,things):
        # serial_write(things_number, pwm 속도):
        size = len(self.sensing_data_list)

        data = -1

        global event_trigger

        if size > 0:
            data = self.sensing_data_list[size-1]
            print("raw data > ", data)
            # print("type >", type(data))
            data = round(data)
            data = int(data)

        if data > Threshole:
            things.serial_writeline(128 + data)
            print("Too many dust, PWM > ", 200 + data)

            event_trigger = True

        else:
            event_trigger = False

        pass

    # 각 장치들 라운드 로빈 스케줄링
    def serial_scheduling(self):
        while main_loop:

            # 역활 구분하여 스케줄링
            for things in self.things_list:
                #print("this role is ",things.role)

                if things.role == "dust sensor":
                    self.sensor_scheduling(things)

                elif things.role == "fan":
                    #상황처리테이블
                    self.fan_scheduling(things)

    # 특정 장치에 대하여 값 보내기
    def serial_write(self, things_number, data):
        self.things_list[things_number].serial_readline(data)

    # 가용 COM포트번호 가져오기
    def serial_ports(self):
        """ Lists serial port names
            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """

        os_name = platform.system()
        print("os name ", os_name)

        if sys.platform.startswith('win'):
            print("windows os")
            ports = ['COM%s' % (i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            print("linux os")
            # this excludes your current terminal "/dev/tty"
            # USB COM 추가
            ports = glob.glob('/dev/tty[A-Za-z]*')
            # ports = ['/dev/ttyUSB%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('darwin'):
            print("mac os")
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')
            print("unknown os")

        result = []

        print("find total port > ", len(ports))
        for port in ports:
            try:

                if os_name is "Windows" or "USB" in port:
                    s = serial.Serial(port)
                    s.close()
                    result.append(port)
                    print("Serial port: ", port, "  add port list")

                else:
                    print("Serial port: ", port, "  unknwon port")

            except (OSError, serial.SerialException):
                pass

        print("Serial port scan done \n\n\n")
        return result


######################          클래스 끝          #########################################

# 관리하는 객체 생성
manager = ThingsMangement()

manager.serial_scheduling() #스케줄링하기