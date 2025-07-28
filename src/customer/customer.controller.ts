import { Controller, Post, Get, Body } from '@nestjs/common';
import { CustomerService } from './customer.service';
import { CreateCustomerDto } from './dto/create-customer.dto';
import { ApiTags, ApiOperation } from '@nestjs/swagger';

@ApiTags('clientes')
@Controller('clientes')
export class CustomerController {
  constructor(private readonly customerService: CustomerService) {}

  @Post()
  @ApiOperation({ summary: 'Crear un nuevo cliente' })
  create(@Body() dto: CreateCustomerDto) {
    return this.customerService.create(dto);
  }

  @Get()
  @ApiOperation({ summary: 'Listar todos los clientes' })
  findAll() {
    return this.customerService.findAll();
  }
}
