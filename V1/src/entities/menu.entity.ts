import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';
import { ApiProperty } from '@nestjs/swagger';

@Entity()
export class Menu {
  @PrimaryGeneratedColumn()
  @ApiProperty({ description: 'ID autogenerado del menú', example: 1 })
  id: number;

  @Column()
  @ApiProperty({ description: 'Nombre del platillo o bebida', example: 'Pizza Margarita' })
  name: string;

  @Column('double precision')
  @ApiProperty({ description: 'Precio del ítem en dólares', example: 12.5 })
  price: number;

  @Column()
  @ApiProperty({ description: 'Contenido del platillo', example: 'Queso, tomate, albahaca' })
  content: string;

  @Column({ default: true })
  @ApiProperty({ description: 'Indica si el ítem está activo o no', example: true })
  active: boolean;

  @Column({ default: false })
  @ApiProperty({ description: 'Indica si es agua', example: false })
  water: boolean;
}


