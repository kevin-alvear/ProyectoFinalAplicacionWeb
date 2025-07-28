import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToMany,
  JoinTable,
  ManyToOne,
  TableInheritance,
  ChildEntity,
} from 'typeorm';
import { Menu } from '../entities/menu.entity';
import { Customer } from '../entities/customer.entity';

@Entity()
@TableInheritance({ column: { type: 'varchar', name: 'type' } }) // Para Single Table Inheritance
export abstract class AbstractOrder {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'timestamp' })
  date: Date;

  @Column()
  waiter: string;

  @Column()
  peopleQty: number;

  @Column('double precision', { default: 0 })
  totalPayment: number;

  @Column({ default: false })
  paid: boolean;

  @ManyToMany(() => Menu)
  @JoinTable()
  menus: Menu[];

  abstract calculateTotalPayment(): void;

  toString(): string {
    return `Order #${this.id} by waiter ${this.waiter} for ${this.peopleQty} people`;
  }
}
