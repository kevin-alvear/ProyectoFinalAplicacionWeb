import { Injectable, NotFoundException } from '@nestjs/common';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';
import { CreateTakeAwayOrderDto } from './dto/create-takeaway-order.dto';
import { CreateShippingOrderDto } from './dto/create-shipping-order.dto';
import { CreateEatInOrderDto } from './dto/create-eatin-order.dto';


import { TakeAwayOrder } from '../entities/takeaway-order.entity';
import { ShippingOrder } from '../entities/shipping-order.entity';
import { EatInOrder } from '../entities/eat-in-order.entity';

import { Menu } from '../entities/menu.entity';
import { Customer } from '../entities/customer.entity';
import { Table } from '../entities/table.entity';

@Injectable()
export class OrderService {
    constructor(
        @InjectRepository(TakeAwayOrder)
        private takeawayRepo: Repository<TakeAwayOrder>,

        @InjectRepository(ShippingOrder)
        private shippingRepo: Repository<ShippingOrder>,

        @InjectRepository(EatInOrder)
        private eatInRepo: Repository<EatInOrder>,
        @InjectRepository(Menu)
        private menuRepo: Repository<Menu>,

        @InjectRepository(Customer)
        private customerRepo: Repository<Customer>,

        @InjectRepository(Table)
        private tableRepo: Repository<Table>,
    ) { }

    async createTakeAway(dto: CreateTakeAwayOrderDto): Promise<TakeAwayOrder> {
        const menus = await this.menuRepo.findByIds(dto.menus);
        if (menus.length === 0) {
            throw new NotFoundException('Menus not found');
        }

        const order = new TakeAwayOrder();
        order.date = new Date(dto.date);
        order.waiter = dto.waiter;
        order.peopleQty = dto.peopleQty;
        order.paid = dto.paid;
        order.menus = menus;
        order.calculateTotalPayment();

        return this.takeawayRepo.save(order);
    }

    async createShipping(dto: CreateShippingOrderDto): Promise<ShippingOrder> {
        const menus = await this.menuRepo.findByIds(dto.menus);
        if (menus.length === 0) {
            throw new NotFoundException('Menus not found');
        }

        let customer: Customer | null = null;
        if (dto.customerId) {
            customer = await this.customerRepo.findOne({ where: { id: dto.customerId } });
            if (!customer) throw new NotFoundException('Customer not found');
        }

        const order = new ShippingOrder();
        order.date = new Date(dto.date);
        order.waiter = dto.waiter;
        order.peopleQty = dto.peopleQty;
        order.paid = dto.paid;
        order.menus = menus;
        order.shippingAddress = dto.shippingAddress;
        order.riderName = dto.riderName;

        if (customer) {
            order.customer = customer;
        }

        order.calculateTotalPayment();

        return this.shippingRepo.save(order);
    }


    async createEatIn(dto: CreateEatInOrderDto): Promise<EatInOrder> {
        const menus = await this.menuRepo.findByIds(dto.menus);
        if (menus.length === 0) {
            throw new NotFoundException('Menus not found');
        }

        const tables = await this.tableRepo.findByIds(dto.tables);
        if (tables.length === 0) {
            throw new NotFoundException('Tables not found');
        }

        let customer: Customer | null = null;
        if (dto.customerId) {
            customer = await this.customerRepo.findOne({ where: { id: dto.customerId } });
            if (!customer) throw new NotFoundException('Customer not found');
        }

        const order = new EatInOrder();
        order.date = new Date(dto.date);
        order.waiter = dto.waiter;
        order.peopleQty = dto.peopleQty;
        order.paid = dto.paid;
        order.menus = menus;
        order.tables = tables;

        if (customer) {
            order.customer = customer;
        }

        order.calculateTotalPayment();

        return this.eatInRepo.save(order);
    }


    findAllTakeAway() {
        return this.takeawayRepo.find({ relations: ['menus'] });
    }

    findAllShipping() {
        return this.shippingRepo.find({ relations: ['menus', 'customer'] });
    }

    findAllEatIn() {
        return this.eatInRepo.find({ relations: ['menus', 'customer', 'tables'] });
    }
}
