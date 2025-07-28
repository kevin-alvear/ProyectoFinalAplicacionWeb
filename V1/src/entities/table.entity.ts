import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity()
export class Table {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  name: string;

  @Column()
  description: string;

  @Column()
  qty: number;

  @Column({ default: false })
  busy: boolean;
}
