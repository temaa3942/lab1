from typing import List
import json
import xml.etree.ElementTree as ET

# ========================= ИСКЛЮЧЕНИЯ =========================
class VehicleError(Exception):
    """Базовое исключение для транспортных средств"""
    pass

class InvalidValueError(VehicleError):
    """Ошибка при недопустимом значении"""
    pass

class NotFoundError(VehicleError):
    """Ошибка при отсутствии объекта"""
    pass

# ========================= БАЗОВЫЕ КЛАССЫ =========================
class Engine:
    """Класс двигателя"""
    def __init__(self, engine_type: str, power: float):
        if power <= 0:
            raise InvalidValueError("Мощность двигателя должна быть больше 0")
        self.engine_type = engine_type
        self.power = power

    def to_dict(self) -> dict:
        return {"engine_type": self.engine_type, "power": self.power}

    @staticmethod
    def from_dict(data: dict) -> "Engine":
        return Engine(data["engine_type"], data["power"])

class Transmission:
    """Класс трансмиссии"""
    def __init__(self, transmission_type: str, gears: int):
        if gears <= 0:
            raise InvalidValueError("Количество передач должно быть > 0")
        self.transmission_type = transmission_type
        self.gears = gears

    def to_dict(self) -> dict:
        return {"transmission_type": self.transmission_type, "gears": self.gears}

    @staticmethod
    def from_dict(data: dict) -> "Transmission":
        return Transmission(data["transmission_type"], data["gears"])

class Wheel:
    """Класс колеса"""
    def __init__(self, size: int):
        if size < 10:
            raise InvalidValueError("Размер колеса слишком маленький")
        self.size = size

    def to_dict(self) -> dict:
        return {"size": self.size}

    @staticmethod
    def from_dict(data: dict) -> "Wheel":
        return Wheel(data["size"])

# ========================= ТРАНСПОРТ =========================
class Vehicle:
    """Базовый класс транспортного средства"""
    def __init__(self, model: str, engine: Engine, transmission: Transmission, wheels: List[Wheel]):
        self.model = model
        self.engine = engine
        self.transmission = transmission
        self.wheels = wheels

    def to_dict(self) -> dict:
        return {
            "type": "Vehicle",
            "model": self.model,
            "engine": self.engine.to_dict(),
            "transmission": self.transmission.to_dict(),
            "wheels": [w.to_dict() for w in self.wheels]
        }

    @staticmethod
    def from_dict(data: dict) -> "Vehicle":
        engine = Engine.from_dict(data["engine"])
        transmission = Transmission.from_dict(data["transmission"])
        wheels = [Wheel.from_dict(w) for w in data["wheels"]]
        return Vehicle(data["model"], engine, transmission, wheels)

class Car(Vehicle):
    """Класс легкового автомобиля"""
    def __init__(self, model: str, engine: Engine, transmission: Transmission, wheels: List[Wheel], seats: int):
        super().__init__(model, engine, transmission, wheels)
        self.seats = seats

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"type": "Car", "seats": self.seats})
        return data

    @staticmethod
    def from_dict(data: dict) -> "Car":
        vehicle = Vehicle.from_dict(data)
        return Car(vehicle.model, vehicle.engine, vehicle.transmission, vehicle.wheels, data.get("seats", 4))

class ElectricCar(Car):
    """Электромобиль"""
    def __init__(self, model: str, engine: Engine, transmission: Transmission, wheels: List[Wheel], seats: int, battery_capacity: float):
        super().__init__(model, engine, transmission, wheels, seats)
        self.battery_capacity = battery_capacity

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"type": "ElectricCar", "battery_capacity": self.battery_capacity})
        return data

    @staticmethod
    def from_dict(data: dict) -> "ElectricCar":
        car = Car.from_dict(data)
        return ElectricCar(car.model, car.engine, car.transmission, car.wheels, car.seats, data.get("battery_capacity", 0))

class Bus(Vehicle):
    """Автобус"""
    def __init__(self, model: str, engine: Engine, transmission: Transmission, wheels: List[Wheel], capacity: int, double_decker: bool):
        super().__init__(model, engine, transmission, wheels)
        self.capacity = capacity
        self.double_decker = double_decker

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"type": "Bus", "capacity": self.capacity, "double_decker": self.double_decker})
        return data

    @staticmethod
    def from_dict(data: dict) -> "Bus":
        vehicle = Vehicle.from_dict(data)
        return Bus(vehicle.model, vehicle.engine, vehicle.transmission, vehicle.wheels, data.get("capacity", 20), data.get("double_decker", False))

class Motorcycle(Vehicle):
    """Мотоцикл"""
    def __init__(self, model: str, engine: Engine, transmission: Transmission, wheels: List[Wheel], moto_type: str):
        super().__init__(model, engine, transmission, wheels)
        self.moto_type = moto_type

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"type": "Motorcycle", "moto_type": self.moto_type})
        return data

    @staticmethod
    def from_dict(data: dict) -> "Motorcycle":
        vehicle = Vehicle.from_dict(data)
        return Motorcycle(vehicle.model, vehicle.engine, vehicle.transmission, vehicle.wheels, data.get("moto_type", "Unknown"))

# ========================= ХРАНИЛИЩЕ =========================
class VehicleStorage:
    """Хранилище транспортных средств"""
    def __init__(self):
        self.vehicles: List["Vehicle"] = []

    def add(self, vehicle: "Vehicle"):
        self.vehicles.append(vehicle)

    def get_all(self) -> List["Vehicle"]:
        return self.vehicles

    def save_json(self, filename: str):
        data = [v.to_dict() for v in self.vehicles]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_json(self, filename: str):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print("Файл JSON не найден, создаём новое хранилище")
            self.vehicles = []
            return

        self.vehicles = []
        for item in data:
            t = item.get("type", "Vehicle")
            if t == "Car":
                self.vehicles.append(Car.from_dict(item))
            elif t == "ElectricCar":
                self.vehicles.append(ElectricCar.from_dict(item))
            elif t == "Bus":
                self.vehicles.append(Bus.from_dict(item))
            elif t == "Motorcycle":
                self.vehicles.append(Motorcycle.from_dict(item))
            else:
                self.vehicles.append(Vehicle.from_dict(item))

    def save_xml(self, filename: str):
        root = ET.Element("Vehicles")
        for v in self.vehicles:
            veh_type = v.to_dict().get("type", "Vehicle")
            veh_elem = ET.SubElement(root, veh_type)
            ET.SubElement(veh_elem, "model").text = v.model
            # Engine
            eng_elem = ET.SubElement(veh_elem, "engine")
            ET.SubElement(eng_elem, "type").text = v.engine.engine_type
            ET.SubElement(eng_elem, "power").text = str(v.engine.power)
            # Transmission
            trans_elem = ET.SubElement(veh_elem, "transmission")
            ET.SubElement(trans_elem, "type").text = v.transmission.transmission_type
            ET.SubElement(trans_elem, "gears").text = str(v.transmission.gears)
            # Wheels
            wheels_elem = ET.SubElement(veh_elem, "wheels")
            for w in v.wheels:
                ET.SubElement(wheels_elem, "wheel").text = str(w.size)
            # Дополнительные поля
            d = v.to_dict()
            for key in d:
                if key not in ["type", "model", "engine", "transmission", "wheels"]:
                    ET.SubElement(veh_elem, key).text = str(d[key])
        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

    def load_xml(self, filename: str):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except FileNotFoundError:
            print("Файл XML не найден, создаём новое хранилище")
            self.vehicles = []
            return

        self.vehicles = []
        for veh in root:
            vehicle_type = veh.tag
            model = veh.findtext("model", default="Unknown")
            engine_type = veh.findtext("engine/type", default="Unknown")
            power = float(veh.findtext("engine/power", default="0"))
            engine = Engine(engine_type, power)
            trans_type = veh.findtext("transmission/type", default="Manual")
            gears = int(veh.findtext("transmission/gears", default="1"))
            transmission = Transmission(trans_type, gears)
            wheels = [Wheel(int(w.text)) for w in veh.find("wheels")]

            if vehicle_type == "Car":
                seats = int(veh.findtext("seats", default="4"))
                self.vehicles.append(Car(model, engine, transmission, wheels, seats))
            elif vehicle_type == "ElectricCar":
                seats = int(veh.findtext("seats", default="4"))
                battery = float(veh.findtext("battery_capacity", default="0"))
                self.vehicles.append(ElectricCar(model, engine, transmission, wheels, seats, battery))
            elif vehicle_type == "Bus":
                capacity = int(veh.findtext("capacity", default="20"))
                double = veh.findtext("double_decker", default="False") == "True"
                self.vehicles.append(Bus(model, engine, transmission, wheels, capacity, double))
            elif vehicle_type == "Motorcycle":
                moto_type = veh.findtext("moto_type", default="Unknown")
                self.vehicles.append(Motorcycle(model, engine, transmission, wheels, moto_type))
            else:
                self.vehicles.append(Vehicle(model, engine, transmission, wheels))


# ========================= ПРИМЕР ИСПОЛЬЗОВАНИЯ =========================
if __name__ == "__main__":
    storage = VehicleStorage()

    # Загружаем старые данные (JSON)
    storage.load_json("vehicles.json")

    # Создаём новый объект
    engine = Engine("Electric", 200)
    transmission = Transmission("Automatic", 1)
    wheels = [Wheel(19) for _ in range(4)]
    new_car = ElectricCar("Tesla Model 3", engine, transmission, wheels, seats=5, battery_capacity=75)

    # Добавляем в хранилище
    storage.add(new_car)

    # Сохраняем все объекты
    storage.save_json("vehicles.json")
    storage.save_xml("vehicles.xml")

    print("Все объекты успешно сохранены в JSON и XML.")
