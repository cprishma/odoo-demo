from odoo import models, fields


class Car(models.Model):
    _name = "car.car"
    image = fields.Image(string='image')
    name = fields.Char(string="car name")
    horse_power = fields.Integer(string="horse power")
    door_number = fields.Integer(string="door number")
    driver_id = fields.Many2one('res.partner', string='driver')
    Parking_ids = fields.Many2one('parking.parking', string='Parking')
    features_ids = fields.Many2many('car.features', string='Features')
    total_speed = fields.Integer(string='Total speed', compute='get_total_speed')
    say_hi = fields.Char(string="Message", compute="say_hello")
    status = fields.Selection([('new', 'New'), ('used', 'Used'), ('sold', 'Sold')], string='status', default='new')

    def set_car_to_used(self):
        self.status = "used"

    def set_car_to_sold(self):
        self.status = "sold"

    def say_hello(self):
        self.say_hi = 'Hello ' + self.driver_id.name

    def get_total_speed(self):
        self.total_speed = self.horse_power * 50


class Parking(models.Model):
    _name = "parking.parking"
    name = fields.Char(string='name')
    car_ids = fields.One2many('car.car', 'Parking_ids', string='Cars')


class CarFeatures(models.Model):
    _name = "car.features"
    name = fields.Char(string="name")
