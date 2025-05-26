# 修复版本的API测试函数
@app.post("/api/test_api_connection")
async def test_api_connection(request: TestAPIRequest, username: str = Depends(verify_token)):
    """测试API连接"""
    try:
        logger.info("开始测试API连接")
        api_url = request.api_url
        api_key = request.api_key
        api_model = request.api_model or "deepseek/deepseek-chat"
        api_timeout = request.api_timeout or 10
        
        logger.debug(f"测试API连接: URL={api_url}, 模型={api_model}, API Key={'已提供' if api_key else '未提供'}, Timeout={api_timeout}")
        
        if not api_url:
            logger.warning("未提供API URL")
            raise HTTPException(status_code=400, detail="请提供API URL")
            
        if not api_key:
            logger.warning("未提供API Key")
            raise HTTPException(status_code=400, detail="请提供API Key")
            
        # 构建API URL
        test_url = APIUtils.format_api_url(api_url)
        logger.debug(f"完整API测试URL: {test_url}")
        
        # 使用异步HTTP客户端发送测试请求
        async with httpx.AsyncClient(timeout=float(api_timeout)) as client:
            response = await client.post(
                test_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": api_model,
                    "messages": [
                        {"role": "user", "content": "Hello, this is a test message. Please respond with 'API connection successful'."}
                    ],
                    "max_tokens": 20
                }
            )
        
        logger.info(f"API响应状态码: {response.status_code}")
        logger.debug(f"API响应内容: {response.text[:200]}...")
        
        # 检查响应
        if response.status_code == 200:
            logger.info(f"API 连接测试成功: {response.status_code}")
            return {"success": True, "message": "API 连接测试成功"}
        else:
            # 安全地解析错误响应
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', '未知错误')
            except:
                # 如果无法解析JSON，使用响应文本
                error_message = response.text[:200] if response.text else f"HTTP {response.status_code} 错误"
            
            logger.warning(f"API连接测试失败: {response.status_code} - {error_message}")
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": f"API 连接测试失败: {error_message}", "status_code": response.status_code}
            )
            
    except httpx.RequestError as e:
        logger.error(f"API 连接请求错误: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": f"请求错误: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"测试 API 连接时出错: {str(e)}")
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"API 测试连接时出错: {str(e)}"}
        )