// 全局变量
var currentPage = 1;
var perPage = 10;
var totalPages = 1; // 初始总页数

// fetchData 函数
function fetchData() {
    $.ajax({
        url: '/db/data/page',
        type: 'GET',
        data: {page: currentPage, per_page: perPage},
        dataType: 'json',
        success: function(data) {
            displayData(data.data);
            totalPages = data.total_pages;
            setupPagination(data.total_pages);
        },
        error: function(xhr, status, error) {
            console.error('Error fetching data: ' + error);
            $('#fans-data > tbody').empty().append('<tr><td colspan="11">加载数据失败，请稍后重试。</td></tr>');
        }
    });
}


// setupPagination 函数
function setupPagination(totalPages) {
    var pageSelect = $('#pageSelect');
    pageSelect.empty(); // 清空当前的页码选项
    for (var i = 1; i <= totalPages; i++) {
        pageSelect.append('<option value="' + i + '">' + i + '</option>'); // 添加新的页码选项
    }
    pageSelect.val(currentPage); // 设置当前选中的页码

    // 由于页面总数可能发生变化，需要更新分页按钮的状态
    updatePaginationButtons(currentPage, totalPages);
}


// changePage 函数
function changePage(direction) {
    if (direction === -1 && currentPage === 1) { // 如果是向前翻页且当前是第一页
        // 禁用上一页按钮
        $('.pagination-button:first').attr('disabled', 'disabled');
        return; // 不进行翻页操作
    } else if (direction === 1 && currentPage === totalPages) { // 如果是向后翻页且当前是最后一页
        // 禁用下一页按钮
        $('.pagination-button:last').attr('disabled', 'disabled');
        return; // 不进行翻页操作
    }
    // 否则，正常翻页
    currentPage += direction;
    fetchData();
    
    // 翻页后，检查并更新按钮状态
    updatePaginationButtons();
}

function updatePaginationButtons() {
    // 如果不是第一页，启用上一页按钮
    if (currentPage > 1) {
        $('.pagination-button:first').prop('disabled', false);
    } else {
        $('.pagination-button:first').prop('disabled', true);
    }

    // 如果不是最后一页，启用下一页按钮
    if (currentPage < totalPages) {
        $('.pagination-button:last').prop('disabled', false);
    } else {
        $('.pagination-button:last').prop('disabled', true);
    }
}

// jumpToPage 函数
function jumpToPage() {
    currentPage = parseInt($('#pageSelect').val());
    fetchData();
}

// 确保 $(document).ready 只绑定一次 fetchData
$(document).ready(function() {
    fetchData(); // 初始化数据加载
    setupPagination(totalPages); // 初始化分页控件
});


    // 查询功能的数据显示函数，仅展示查询结果
    function displayData_select(data) {
        var tbody = $('#fans-data > tbody');
        tbody.empty(); // 清空现有的表格内容

        if (!data || data.length === 0) {
            tbody.append('<tr><td colspan="所有列的数量">暂无数据。</td></tr>');
            return;
        }

        // 构建表头
        var thead = $('#fans-data > thead');
        if (thead.length === 0) {
            var headerRow = $('<tr></tr>');
            // 假设返回的数据是一个对象数组，每个对象的键即为列名
            Object.keys(data[0]).forEach(function(key) {
                headerRow.append($('<th></th>').text(key));
            });
            thead.append(headerRow);
        }

        // 将获取的数据插入到表格中
        $.each(data, function(index, row) {
            tbody.append(showData(row));
        });
    }   

    function showData(row) {
        // 转换时间戳为可读格式
        var timestamp = new Date(row[12]).getTime() + (new Date().getTimezoneOffset() * 60000);
        var localtime = new Date(timestamp).toLocaleString();
        return (
            '<tr>' +
            '<td>' + row[0] + '</td>' +
            '<td>' + row[1] + '</td>' +
            '<td>' + row[2] + '</td>' +
            '<td>' + row[3] + '</td>' +
            '<td>' + row[4] + '</td>' +
            '<td>' + row[5] + '</td>' +
            '<td>' + row[6] + '</td>' +
            '<td>' + row[7] + '</td>' +
            '<td>' + row[8] + '</td>' +
            '<td>' + row[9] + '</td>' +
            '<td>' + row[10] + '</td>' +
            '<td>' + row[11] + '</td>' +
            '<td>' + localtime + '</td>' +
            '</tr>'
        );
    }


    // 用于显示数据的函数
    function displayData(data) {
        var tbody = $('#fans-data > tbody');
        tbody.empty(); // 清空现有的表格内容

        if (!data || data.length === 0) {
            tbody.append('<tr><td colspan="所有列的数量">暂无数据。</td></tr>');
            return;
        }

        // 构建表头
        var thead = $('#fans-data > thead');
        if (thead.length === 0) {
            var headerRow = $('<tr></tr>');
            // 假设返回的数据是一个对象数组，每个对象的键即为列名
            Object.keys(data[0]).forEach(function(key) {
                headerRow.append($('<th></th>').text(key));
            });
            thead.append(headerRow);
        }

        // 将获取的数据插入到表格中
        $.each(data, function(index, row) {
            tbody.append(showData(row));
        });
    }   

    // 处理混合ID输入的函数定义
    function parseIdsInput(idsInput) {
        const rangeRegex = /^(\d+)-(\d+)$/;
        let flatList = [];
        let parts = idsInput.split(',').map(part => part.trim()); // 移除空格并分割输入

        parts.forEach(part => {
            const match = part.match(rangeRegex);
            if (match) {
                // 如果是范围，生成范围内的所有ID
                const startId = parseInt(match[1], 10);
                const endId = parseInt(match[2], 10);
                flatList = flatList.concat(Array.from({length: endId - startId + 1}, (v, k) => k + startId));
            } else {
                // 单个ID
                const id = parseInt(part, 10);
                if (!isNaN(id)) {
                    flatList.push(id);
                }
            }
        });

        return flatList;
    }            
   



// 处理增加数据的表单提交
$('#add-data-form').submit(function(event) {
    event.preventDefault();
    var data = {
        // '风机名称': $('#fan-name').val() ,
        // '风机型号': $('#fan-model').val() ,
        '设定转速': $('#set-speed').val() ,
        '实际转速': $('#actual-speed').val() ,
        '速度环补偿系数': $('#speed-compensation').val() ,
        '电流环带宽': $('#current-bandwidth').val() ,
        '观测器补偿系数': $('#observer-compensation').val() ,
        '负载量': $('#load').val() ,
        '输入功率': $('#input_power').val() ,
        '输出功率': $('#output_power').val() ,
        '效率': $('#efficiency').val() ,
        '故障': $('#fault').val()
    };

    $.ajax({
        url: '/db/data',
        type: 'POST',
        data: JSON.stringify({'data_list': [data]}),
        contentType: 'application/json',
        success: function(response) {
            alert(response.message);
            fetchData(); // 刷新表格数据
        },
        error: function(xhr, status, error) {
            console.error('Error inserting data: ' + error);
            alert('数据增加失败，请稍后重试。');
        }
    });
});



// 处理删除数据的表单提交
$('#delete-data-form').submit(function(event) {
    event.preventDefault();
    var idsInput = $('#delete-ids').val(); // 获取混合ID输入

    // 解析混合ID输入
    let ids = parseIdsInput(idsInput);

    // 发送AJAX请求删除数据
    $.ajax({
        url: '/db/data',
        type: 'DELETE',
        data: JSON.stringify({'ids_input': ids}),
        contentType: 'application/json',
        success: function(response) {
            if (response.status === 'success') {
                // 删除成功后，直接调用 fetchData 函数刷新第一页的数据
                currentPage = 1; // 重置当前页为第一页
                fetchData(); 
                alert(response.message);
            } else {
                alert(response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error deleting data: ' + error);
            alert('数据删除失败，请稍后重试。');
        }
    });
});



// 处理修改数据的表单提交
$('#update-data-form').submit(function(event) {
    event.preventDefault();
    var idsInput = $('#update-ids').val(); // 获取混合ID输入
    var parameter = $('#update-parameter').val().trim(); // 获取指定参数
    var value = $('#update-value').val().trim(); // 获取指定参数修改后的值

    // 解析混合ID输入
    let ids = parseIdsInput(idsInput);

    var updateData = {};
    updateData[parameter] = value; // 构造更新数据对象

    // 将ids数组转换为逗号分隔的字符串
    let idsString = ids.join(',');

    // 发送AJAX请求更新数据
    $.ajax({
        url: '/db/data',
        type: 'PUT',
        data: JSON.stringify({'ids': idsString, 'update_data': updateData}),
        contentType: 'application/json',
        success: function(response) {
            // currentPage = 4; // 重置当前页为第一页
            fetchData(); 
            alert(response.message);
        },
        error: function(xhr, status, error) {
            console.error('Error updating data: ' + error);
            alert('数据修改失败，请稍后重试。');
        }
    });
});



// 处理查询数据的表单提交
$('#query-data-form').submit(function(event) {
    event.preventDefault();
    var mixedIdsInput = $('#query-mixed-ids').val(); // 获取混合ID输入
    var conditions = $('#query-conditions').val().trim(); // 获取附加条件输入

    // 解析混合ID输入，支持单个ID、ID列表和ID范围
    let ids_input = parseIdsInput(mixedIdsInput);

    // 构造查询参数
    let params = {
        ids_input: ids_input.join(','), // 将解析后的ID列表转换为字符串
        conditions: conditions // 附加条件
    };

    // 发送AJAX请求
    $.ajax({
        url: '/db/data',
        type: 'GET',
        data: params,
        dataType: 'json',
        success: function(data) {
            // 展示查询结果
            displayData_select(data);
        },
        error: function(xhr, status, error) {
            console.error('Error fetching data: ' + error);
            alert('数据查询失败，请稍后重试。');
        }
    });
});

// 处理数据导出的表单提交
$('#export-data-form').submit(function(event) {
    event.preventDefault();
    var idsInput = $('#export-mixed-ids').val(); // 获取混合ID输入
    console.log(idsInput); // 使用 console.log 替换 print
    var additionalConditions = $('#export-additional-conditions').val().trim(); // 获取附加条件输入
    var filename = $('#export-filename').val().trim(); // 获取文件名输入

    // 解析混合ID输入
    let ids_export = parseIdsInput(idsInput);         

    // 检查文件名是否已指定
    if (!filename) {
        alert('请指定CSV文件名。');
        return;
    }

    // 发送AJAX请求导出数据
    $.ajax({
        url: '/db/export',
        type: 'GET',
        data: {
            filename: filename, // 指定导出的CSV文件名
            ids_input: ids_export.join(','), // 确保这里将数组转换为字符串
            additional_conditions: additionalConditions, // 将附加条件作为查询参数
        },
        dataType: 'json',
        success: function(response) {
            if (response.status === 'success') {
                alert(response.message); // 导出成功提示
            } else {
                alert('导出失败：' + response.message); // 导出失败提示
            }
        },
        error: function(xhr, status, error) {
            console.error('Error exporting data: ' + error);
            alert('数据导出失败，请稍后重试。');
        }
    });
});

// 绑定清除数据按钮的点击事件
$('#clear-data-button').click(function() {
    // 显示确认删除的对话框
    var confirmDelete = confirm("再次确认是否删除整个数据库！");
    if (confirmDelete) {
        // 如果用户点击“是”，则发送请求删除所有数据
        $.ajax({
            url: '/db/clear_data', // 确保这个URL匹配后端定义的路由
            type: 'DELETE',
            success: function(response) {
                if (response.status === 'success') {
                    alert('数据库已清空！');
                    // 刷新页面或执行其他操作，例如重新加载数据
                    fetchData(); // 假设这是刷新表格数据的函数
                } else {
                    alert('删除失败，请稍后重试。');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error deleting data: ' + error);
                alert('数据删除失败，请稍后重试。');
            }
        });
    }
    // 如果用户点击“否”，则不进行任何操作
});     