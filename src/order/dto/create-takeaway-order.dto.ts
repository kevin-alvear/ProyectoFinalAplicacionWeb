import {
  IsString,
  IsInt,
  IsBoolean,
  IsDateString,
  IsArray,
  ArrayNotEmpty,
} from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateTakeAwayOrderDto {
  @ApiProperty({ example: '2025-07-18T12:00:00Z', description: 'Date of the order' })
  @IsDateString()
  date: string;

  @ApiProperty({ example: 'John Doe', description: 'Name of the waiter' })
  @IsString()
  waiter: string;

  @ApiProperty({ example: 4, description: 'Number of people' })
  @IsInt()
  peopleQty: number;

  @ApiProperty({ example: true, description: 'Indicates if the order is paid' })
  @IsBoolean()
  paid: boolean;

  @ApiProperty({ type: [Number], example: [1, 2], description: 'Array of menu IDs' })
  @IsArray()
  @ArrayNotEmpty()
  @IsInt({ each: true })
  menus: number[]; // IDs de menús
}

