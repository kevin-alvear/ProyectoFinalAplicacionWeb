import {
  IsString,
  IsInt,
  IsBoolean,
  IsDateString,
  IsArray,
  ArrayNotEmpty,
  IsOptional,
} from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateEatInOrderDto {
  @ApiProperty({ example: '2025-07-18T12:00:00Z', description: 'Date of the order' })
  @IsDateString()
  date: string;

  @ApiProperty({ example: 'John Doe', description: 'Name of the waiter' })
  @IsString()
  waiter: string;

  @ApiProperty({ example: 5, description: 'Number of people' })
  @IsInt()
  peopleQty: number;

  @ApiProperty({ example: false, description: 'Indicates if the order is paid' })
  @IsBoolean()
  paid: boolean;

  @ApiProperty({ type: [Number], example: [1, 2], description: 'Array of menu IDs' })
  @IsArray()
  @ArrayNotEmpty()
  @IsInt({ each: true })
  menus: number[];

  @ApiProperty({ type: [Number], example: [1, 3], description: 'Array of table IDs' })
  @IsArray()
  @ArrayNotEmpty()
  @IsInt({ each: true })
  tables: number[];

  @ApiPropertyOptional({ example: 2, description: 'Optional customer ID related to this order' })
  @IsInt()
  @IsOptional()
  customerId?: number;
}
