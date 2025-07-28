import { ApiProperty } from '@nestjs/swagger';
import { IsString, IsInt, IsBoolean } from 'class-validator';

export class CreateTableDto {
  @ApiProperty({ example: 'Mesa 1', description: 'Nombre de la mesa' })
  @IsString()
  name: string;

  @ApiProperty({ example: 'Mesa junto a ventana', description: 'Descripción de la mesa' })
  @IsString()
  description: string;

  @ApiProperty({ example: 4, description: 'Cantidad de personas que puede sentar' })
  @IsInt()
  qty: number;

  @ApiProperty({ example: false, description: 'Indica si la mesa está ocupada' })
  @IsBoolean()
  busy: boolean;
}
