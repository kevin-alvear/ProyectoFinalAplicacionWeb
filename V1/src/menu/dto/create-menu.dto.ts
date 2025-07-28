import { IsString, IsBoolean, IsNumber } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateMenuDto {
  @IsString()
  @ApiProperty({ example: 'Coca Cola', description: 'Nombre del ítem del menú' })
  name: string;

  @IsNumber()
  @ApiProperty({ example: 2.5, description: 'Precio del ítem del menú' })
  price: number;

  @IsString()
  @ApiProperty({ example: 'Bebida gaseosa 500ml', description: 'Contenido o descripción del ítem' })
  content: string;

  @IsBoolean()
  @ApiProperty({ example: true, description: 'Indica si está disponible para pedidos' })
  active: boolean;

  @IsBoolean()
  @ApiProperty({ example: false, description: 'Indica si es agua (true si es agua)' })
  water: boolean;
}

