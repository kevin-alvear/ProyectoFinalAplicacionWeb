import { ApiProperty } from '@nestjs/swagger';
import { IsString, IsEmail } from 'class-validator';

export class CreateCustomerDto {
  @ApiProperty({ example: 'Juan Pérez', description: 'Nombre del cliente' })
  @IsString()
  name: string;

  @ApiProperty({ example: 'juan.perez@mail.com', description: 'Email del cliente' })
  @IsEmail()
  email: string;
}
