import { IsString, IsInt, IsBoolean, IsDateString, IsArray } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateBookingDto {
  @ApiProperty({ example: 'Juan Pérez', description: 'Nombre del cliente' })
  @IsString()
  name: string;

  @ApiProperty({ example: '+593987654321', description: 'Número telefónico' })
  @IsString()
  phoneNumber: string;

  @ApiProperty({ example: 4, description: 'Cantidad de personas' })
  @IsInt()
  peopleQty: number;

  @ApiProperty({ example: '2025-07-20T15:00:00Z', description: 'Fecha y hora de la reserva' })
  @IsDateString()
  date: string;

  @ApiProperty({ example: [1, 2], description: 'IDs de las mesas reservadas' })
  @IsArray()
  tables: number[];

  @ApiProperty({ example: false, description: 'Estado de confirmación de la reserva' })
  @IsBoolean()
  confirmed: boolean;
}
