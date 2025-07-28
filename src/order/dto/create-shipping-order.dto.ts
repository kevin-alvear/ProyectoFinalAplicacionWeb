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

export class CreateShippingOrderDto {
  @ApiProperty({ example: '2025-07-18T12:00:00Z', description: 'Date of the order' })
  @IsDateString()
  date: string;

  @ApiProperty({ example: 'John Doe', description: 'Name of the waiter' })
  @IsString()
  waiter: string;

  @ApiProperty({ example: 3, description: 'Number of people' })
  @IsInt()
  peopleQty: number;

  @ApiProperty({ example: true, description: 'Indicates if the order is paid' })
  @IsBoolean()
  paid: boolean;

  @ApiProperty({ type: [Number], example: [1, 2], description: 'Array of menu IDs' })
  @IsArray()
  @ArrayNotEmpty()
  @IsInt({ each: true })
  menus: number[];

  @ApiProperty({ example: '123 Main St, City', description: 'Shipping address' })
  @IsString()
  shippingAddress: string;

  @ApiProperty({ example: 'Juan Rider', description: 'Name of the rider' })
  @IsString()
  riderName: string;

  @ApiPropertyOptional({ example: 1, description: 'Optional customer ID related to this order' })
  @IsInt()
  @IsOptional()
  customerId?: number;
}

