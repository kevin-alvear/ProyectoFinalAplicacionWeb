import { ChildEntity } from 'typeorm';
import { AbstractOrder } from './order.entity';

@ChildEntity()
export class TakeAwayOrder extends AbstractOrder {
  calculateTotalPayment() {
    this.totalPayment = this.menus.reduce((acc, menu) => acc + menu.price, 0);
  }
}
