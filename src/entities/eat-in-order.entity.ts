import { ChildEntity, ManyToMany, JoinTable, ManyToOne } from 'typeorm';
import { AbstractOrder } from './order.entity';
import { Table } from '../entities/table.entity';
import { Customer } from '../entities/customer.entity';

@ChildEntity()
export class EatInOrder extends AbstractOrder {
  @ManyToMany(() => Table)
  @JoinTable()
  tables: Table[];

  @ManyToOne(() => Customer)
  customer: Customer;

  calculateTotalPayment() {
    this.totalPayment = this.menus.reduce((acc, menu) => acc + menu.price, 0);
  }
}
