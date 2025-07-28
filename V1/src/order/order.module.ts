import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';

import { OrderService } from './order.service';
import { OrderController } from './order.controller';
import { Menu } from '../entities/menu.entity';
import { AbstractOrder } from '../entities/order.entity';
import { TakeAwayOrder } from '../entities/takeaway-order.entity';
import { ShippingOrder } from '../entities/shipping-order.entity';
import { EatInOrder } from '../entities/eat-in-order.entity';
import { Customer } from '../entities/customer.entity';
import { Table } from '../entities/table.entity';

@Module({
  imports: [
    TypeOrmModule.forFeature([
      AbstractOrder,
      TakeAwayOrder,
      ShippingOrder,
      EatInOrder,
      Menu,
      Customer,
      Table,
    ]),
  ],
  providers: [OrderService],
  controllers: [OrderController],
})
export class OrderModule {}

