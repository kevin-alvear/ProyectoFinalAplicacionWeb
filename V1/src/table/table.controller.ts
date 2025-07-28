import { Controller, Get, Post, Body } from '@nestjs/common';
import { TableService } from './table.service';
import { CreateTableDto } from './dto/create-table.dto';
import { ApiTags, ApiOperation } from '@nestjs/swagger';

@ApiTags('salas')
@Controller('salas')
export class TableController {
  constructor(private readonly tableService: TableService) {}

  @Get()
  @ApiOperation({ summary: 'Listar todas las salas' })
  findAll() {
    return this.tableService.findAll();
  }

  @Post()
  @ApiOperation({ summary: 'Crear una nueva sala' })
  create(@Body() dto: CreateTableDto) {
    return this.tableService.create(dto);
  }
}

