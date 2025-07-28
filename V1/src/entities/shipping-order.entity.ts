import { ChildEntity, Column, ManyToOne } from 'typeorm';
import { AbstractOrder } from './order.entity';
import { Customer } from '../entities/customer.entity';

@ChildEntity()
export class ShippingOrder extends AbstractOrder {
  @Column()
  shippingAddress: string;

  @Column()
  riderName: string;

  @ManyToOne(() => Customer)
  customer: Customer;

  calculateTotalPayment() {
    this.totalPayment = this.menus.reduce((acc, menu) => acc + menu.price, 0);
  }
}
