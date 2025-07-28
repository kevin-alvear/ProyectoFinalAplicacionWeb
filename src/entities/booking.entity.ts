import {
  Entity, PrimaryGeneratedColumn, Column, ManyToMany, JoinTable, ManyToOne,
} from 'typeorm';
import { Table } from './table.entity';
import { Customer } from './customer.entity';

@Entity()
export class Booking {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @Column()
  phoneNumber: string;

  @Column()
  peopleQty: number;

  @Column({ type: 'timestamp' })
  date: Date;

  @Column({ default: false })
  confirmed: boolean;

  @ManyToMany(() => Table)
  @JoinTable()
  tables: Table[];

  @ManyToOne(() => Customer, (customer) => customer.bookings, { nullable: true })
  customer: Customer;
}
